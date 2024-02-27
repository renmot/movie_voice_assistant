# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions
import logging
import os
import re
from typing import Text, Dict, Any, List, cast, Callable

from elasticsearch import Elasticsearch
from rasa_sdk import Tracker, utils
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.knowledge_base.actions import ActionQueryKnowledgeBase
from rasa_sdk.knowledge_base.utils import SLOT_OBJECT_TYPE, SLOT_ATTRIBUTE, \
    SLOT_LAST_OBJECT_TYPE, reset_attribute_slots, \
    SLOT_MENTION, SLOT_LAST_OBJECT, SLOT_LISTED_OBJECTS, get_object_name
from rasa_sdk.types import DomainDict

from actions.storage import DefaultAttribute, DocumentType, \
    ElasticsearchKnowledgeBase, RangeAttribute, TextAttribute

logger = logging.getLogger(__name__)

SLOT_LIMIT = "limit"
    

class MovieDocumentType(DocumentType):
    def __init__(self, index: Text) -> None:
        attributes = {
            "title": TextAttribute("title"),
            "publication_year": RangeAttribute("publication_year"),
            "genre": TextAttribute("genre"),
            "description": DefaultAttribute("description"),
            "imdb_rating": RangeAttribute("imdb_rating"),
            "actors_names": TextAttribute("actors_names"),
            "director": TextAttribute("director")
        }
        super().__init__(index, attributes)

    def to_string(self, document: Dict[Text, Any]) -> Text:
        return f'{document["title"]}'


def sanitize(text: Text) -> Text:
    return re.sub(r"[{}\[\]\']", "", text)


def get_attribute_slots(
        tracker: "Tracker", object_attributes: List[Text]
) -> List[Dict[Text, Text]]:
    """
    Copied from rasa_sdk.knowledge_base.utils  and overridden
    as we also need to return the entity role for range queries.

    If the user mentioned one or multiple attributes of the provided object_type in
    an utterance, we extract all attribute values from the tracker and put them
    in a list. The list is used later on to filter a list of objects.

    For example: The user says 'What Italian restaurants do you know?'.
    The NER should detect 'Italian' as 'cuisine'.
    We know that 'cuisine' is an attribute of the object type 'restaurant'.
    Thus, this method returns [{'name': 'cuisine', 'value': 'Italian'}] as
    list of attributes for the object type 'restaurant'.

    Args:
        tracker: the tracker
        object_attributes: list of potential attributes of object

    Returns: a list of attributes
    """
    attributes = []

    for attr in object_attributes:
        attr_val = tracker.get_slot(attr) if attr in tracker.slots else None
        if attr_val is not None:
            entities = tracker.latest_message.get("entities", [])
            role = [e['role'] for e in entities if e['entity'] == attr and e['value'] == attr_val and 'role' in e]
            role = role[0] if len(role) else None
            attributes.append({"name": attr, "value": attr_val, "role": role})

    return attributes


class ActionElasticsearchKnowledgeBase(ActionQueryKnowledgeBase):
    def __init__(self):
        document_types: Dict[Text, DocumentType] = {
            "movie": MovieDocumentType("movie")
        }
        host = os.environ['ES_HOST']
        knowledge_base = ElasticsearchKnowledgeBase(
            document_types=document_types,
            es=Elasticsearch(
                hosts=[host],
                request_timeout=60,
            ),
        )

        super().__init__(knowledge_base)

    async def run(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: "DomainDict",
    ) -> List[Dict[Text, Any]]:
        """
        Copied from ActionQueryKnowledgeBase and overridden because we
        want to perform a join query if last and current object types
        differ but a mention is present

        Executes this action. If the user ask a question about an attribute,
        the knowledge base is queried for that attribute. Otherwise, if no
        attribute was detected in the request or the user is talking about a new
        object type, multiple objects of the requested type are returned from the
        knowledge base.

        Args:
            dispatcher: the dispatcher
            tracker: the tracker
            domain: the domain

        Returns: list of slots

        """
        object_type = tracker.get_slot(SLOT_OBJECT_TYPE)
        last_object_type = tracker.get_slot(SLOT_LAST_OBJECT_TYPE)
        attribute = tracker.get_slot(SLOT_ATTRIBUTE)
        has_mention = tracker.get_slot(SLOT_MENTION) is not None

        new_request = object_type != last_object_type

        if not object_type:
            # object type always needs to be set as this is needed to query the
            # knowledge base
            dispatcher.utter_message(template="utter_ask_rephrase")
            return []

        if last_object_type and new_request and has_mention:
            return await self._query_join_objects(dispatcher, object_type, last_object_type, tracker)
        elif not attribute:
            return await self._query_objects(dispatcher, object_type, tracker)
        elif attribute:
            return await self._query_attribute(
                dispatcher, object_type, attribute, tracker
            )

        dispatcher.utter_message(template="utter_ask_rephrase")

        return []

    async def _query_objects(
            self, dispatcher: CollectingDispatcher, object_type: Text,
            tracker: Tracker
    ) -> List[Dict]:
        """
        Copied from ActionQueryKnowledgeBase and overridden
        in order to introduce LIMIT parameter

        Queries the knowledge base for objects of the requested object type and
        outputs those to the user. The objects are filtered by any attribute the
        user mentioned in the request.

        Args:
            dispatcher: the dispatcher
            tracker: the tracker

        Returns: list of slots
        """
        object_attributes = await utils.call_potential_coroutine(
            self.knowledge_base.get_attributes_of_object(object_type)
        )

        # get all set attribute slots of the object type to be able to filter the
        # list of objects
        limit = tracker.get_slot(SLOT_LIMIT)
        logger.info(f"Limit is {limit}")
        attributes = get_attribute_slots(tracker, object_attributes)
        var_args = {}
        if limit:
            var_args['limit'] = int(limit)

        # query the knowledge base
        objects = await utils.call_potential_coroutine(
            self.knowledge_base.get_objects(object_type, attributes, **var_args)
        )

        await utils.call_potential_coroutine(
            self.utter_objects(dispatcher, object_type, objects, attributes)
        )

        if not objects:
            return reset_attribute_slots(tracker, object_attributes)

        key_attribute = await utils.call_potential_coroutine(
            self.knowledge_base.get_key_attribute_of_object(object_type)
        )

        last_object = None if len(objects) > 1 else objects[0][key_attribute]

        slots = [
            SlotSet(SLOT_OBJECT_TYPE, object_type),
            SlotSet(SLOT_MENTION, None),
            SlotSet(SLOT_ATTRIBUTE, None),
            SlotSet(SLOT_LAST_OBJECT, last_object),
            SlotSet(SLOT_LAST_OBJECT_TYPE, object_type),
            SlotSet(
                SLOT_LISTED_OBJECTS,
                list(map(lambda e: e[key_attribute], objects))
            ),
            SlotSet(SLOT_LIMIT, None),
        ]

        return slots + reset_attribute_slots(tracker, object_attributes)

    async def utter_objects(
            self,
            dispatcher: CollectingDispatcher,
            object_type: Text,
            objects: List[Dict[Text, Any]],
            attributes: List[Dict[Text, Text]] = None,
    ):
        """
        Utters a response to the user that lists all found objects.

        Args:
            dispatcher: the dispatcher
            object_type: the object type
            objects: the list of objects
        """
        attributes_list = [attribute['name'].replace('_', ' ') + " " + attribute['value'] for attribute in attributes]
        attributes_repr = f" with {', '.join(attributes_list)}" if attributes else ""
        if objects:
            first_sentence=f"I found the following {object_type}s {attributes_repr}"
            logger.info(f"objects are: {objects}")
            object_names = [object["name"] for object in objects]
            object_names_str =  ", ".join(object_names)
            message = first_sentence + ": " + object_names_str
            logger.info(f"message is {message}")

            dispatcher.utter_message(text=message)
            
        else:
            dispatcher.utter_message(
                text=f"I could not find any {object_type}s {attributes_repr}."
            )

    def utter_attribute_value(
            self,
            dispatcher: CollectingDispatcher,
            object_name: Text,
            attribute_name: Text,
            attribute_value: Text,
    ):
        """
        Utters a response that informs the user about the attribute value of the
        attribute of interest.

        Args:
            dispatcher: the dispatcher
            object_name: the name of the object
            attribute_name: the name of the attribute
            attribute_value: the value of the attribute
        """
        if attribute_value:
            dispatcher.utter_message(
                text=f"The {attribute_name.replace('_', ' ')} of '{object_name}': \n\n {sanitize(str(attribute_value))}"
            )
        else:
            dispatcher.utter_message(
                text=f"Did not find a valid value for attribute '{attribute_name.replace('_', ' ')}' for object '{object_name}'."
            )

    async def _query_join_objects(self, dispatcher: CollectingDispatcher, object_type: Text, last_object_type, tracker: Tracker) -> List[Dict]:
        """
        Performs a join query on the knowledge base
        by returning the object of type 'object_type'
        where the key attribute matches the key of the last object in the tracker.

        Args:
            dispatcher: the dispatcher
            tracker: the tracker

        Returns: list of slots
        """

        object_name = get_object_name(
            tracker,
            self.knowledge_base.ordinal_mention_mapping,
            self.use_last_object_mention,
        )

        last_object = await utils.call_potential_coroutine(
            self.knowledge_base.get_object(last_object_type, object_name)
        )

        if not object_name or not object_type or not last_object:
            dispatcher.utter_message(template="utter_ask_rephrase")
            return [SlotSet(SLOT_MENTION, None)]

        object_of_interest = await utils.call_potential_coroutine(
            self.knowledge_base.get_object(object_type, object_name)
        )

        obj_repr = self.knowledge_base.document_types[object_type].to_string(object_of_interest)
        last_obj_repr = self.knowledge_base.document_types[last_object_type].to_string(last_object)

        dispatcher.utter_message(
            text=f"{obj_repr} is the {object_type} for {last_object_type} {last_obj_repr}."
        )

        slots = [
            SlotSet(SLOT_OBJECT_TYPE, last_object_type),
            SlotSet(SLOT_MENTION, None),
            SlotSet(SLOT_ATTRIBUTE, None),
            SlotSet(SLOT_LAST_OBJECT, object_name),
            SlotSet(SLOT_LAST_OBJECT_TYPE, last_object_type),
            SlotSet(SLOT_LIMIT, None),
        ]

        return slots
