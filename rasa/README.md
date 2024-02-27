# Movie Voice Assistant

## How to train a new model locally

Install Spacy models and Rasa

```
python3.7 -m venv venv
source venv/bin/activate
pip3 install --upgrade pip
pip3 install rasa==2.8.21
pip3 install spacy==2.3.5
python3 -m spacy download en_core_web_md
python3 -m spacy link en_core_web_md en
```

Train a new model

`rasa train --augmentation 0`

