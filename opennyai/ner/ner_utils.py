from opennyai.ner.InLegalNER.InLegalNER import InLegalNER
import copy
from hashlib import sha256


def load(model_name: str = 'en_legal_ner_trf', use_gpu: bool = True):
    """Returns object of InLegalNER class.
     It is used for loading InLegalNER model in memory.
    Args:
        model_name (string): Accepts a model name of spacy as InLegalNER that will be used for NER inference
        available models are 'en_legal_ner_trf', 'en_legal_ner_sm'
        use_gpu (bool): Functionality to give a choice whether to use GPU for inference or not
         Setting it True doesn't ensure GPU will be utilized it need proper support libraries as mentioned in
         documentation
    """
    AVAILABLE_LEGAL_NER_MODELS = ['en_legal_ner_trf', 'en_legal_ner_sm']
    if model_name not in AVAILABLE_LEGAL_NER_MODELS:
        raise RuntimeError(f'{model_name} doesn\'t exit in list of available models {AVAILABLE_LEGAL_NER_MODELS}')
    return InLegalNER(model_name, use_gpu)


def update_json_with_clusters(ls_formatted_doc: dict, precedent_clusters: dict, provision_statute_clusters: list,
                              statute_clusters: dict):
    for entity, _, __, val in provision_statute_clusters:
        for result in ls_formatted_doc['annotations'][0]['result']:
            if result['value']['start'] == entity.start_char and result['value']['end'] == entity.end_char:
                result['meta']['text'].append(str(val))

    for val in statute_clusters.keys():
        for entity in statute_clusters[val]:
            for result in ls_formatted_doc['annotations'][0]['result']:
                if result['value']['start'] == entity.start_char and result['value']['end'] == entity.end_char:
                    result['meta']['text'].append(str(val))

    for val in precedent_clusters.keys():
        for entity in precedent_clusters[val]:
            for result in ls_formatted_doc['annotations'][0]['result']:
                if result['value']['start'] == entity.start_char and result['value']['end'] == entity.end_char:
                    result['meta']['text'].append(str(val))

    return ls_formatted_doc


def get_json_from_spacy_doc(doc) -> dict:
    """Returns dict of InLegalNER doc.
    Args:
        doc: InLegalNER doc
    """
    id = "LegalNER_" + doc.user_data['doc_id']
    output = {'id': id, 'annotations': [{'result': []}],
              'data': {'text': doc.text, 'original_text': doc.user_data['original_text']}}
    for ent in doc.ents:
        import uuid
        uid = uuid.uuid4()
        id = uid.hex
        output['annotations'][0]['result'].append(copy.deepcopy({"id": id, "meta": {"text": []},
                                                                 "type": "labels",
                                                                 "value": {
                                                                     "start": ent.start_char,
                                                                     "end": ent.end_char,
                                                                     "text": ent.text,
                                                                     "labels": [ent.label_],
                                                                 }, "to_name": "text",
                                                                 "from_name": "label"
                                                                 }))

    final_output = update_json_with_clusters(copy.deepcopy(output), doc.user_data['precedent_clusters'],
                                             doc.user_data['provision_statute_clusters'], doc.user_data['statute_clusters'])

    return final_output


ner_displacy_option = {
    'colors': {'COURT': "#bbabf2", 'PETITIONER': "#f570ea", "RESPONDENT": "#cdee81", 'JUDGE': "#fdd8a5",
               "LAWYER": "#f9d380", 'WITNESS': "violet", "STATUTE": "#faea99", "PROVISION": "yellow",
               'CASE_NUMBER': "#fbb1cf", "PRECEDENT": "#fad6d6", 'DATE': "#b1ecf7", 'OTHER_PERSON': "#b0f6a2",
               'ORG': '#a57db5', 'GPE': '#7fdbd4'}}
