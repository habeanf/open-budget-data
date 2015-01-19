###encoding: utf8
import json
import bisect
import logging

class process_entities(object):

    CLEAN_WORDS = [ u'בע"מ',
                    u'בעמ',
                    u"בע'מ",
                    u'(חל"צ)',
                    u'בע"מ.',
                    u'אינק.',
                    u'לימיטד',
                    u'בע"מ"',
                    u'בע,מ',
                    u'עב"מ',
                    u'בע"ם',
                    u'(ע"ר)',
                    u"(ע''ר)",
                    u'בע"מ (חל"צ)',
                  ]
    def __init__(self):
        self.CLEAN_PREFIXES = set()
        for w in self.CLEAN_WORDS:
            for i in range(1,len(w)+1):
                self.CLEAN_PREFIXES.add(" "+w[:i])

    def clean(self,word):
        for p in self.CLEAN_PREFIXES:
            if word.endswith(p):
                return word[:-len(p)]
        return word

    def process(self,inputs,outputs,name_key=None, processed_file=None, id_keys=None ):
        entities_file, match_file = inputs
        used_entities_file = outputs

        entities = []
        for line in file(entities_file):
            entities.append(json.loads(line))
        entities.sort(key=lambda x:self.clean(x['name']))
        entity_names = [self.clean(x['name']) for x in entities]

        processed_file = file(processed_file,'w')
        used_entities_file = file(used_entities_file,'w')
        matches = 0
        for line in file(match_file):
            line = json.loads(line)
            match_value = self.clean(line.get(name_key))
            found = None
            if match_value is not None:
                i = bisect.bisect_left(entity_names, match_value)
                if i != len(entity_names):
                    found = entities[i]
            if found is not None:
                clean_found = self.clean(found['name'])
                if clean_found==match_value or (len(match_value) > 30 and clean_found.startswith(match_value)):
                    matches += 1#print "||%s|||%s" % (match_value, clean_found)
                    rec = {}
                    for id_key in id_keys:
                        rec[id_key] = line[id_key]
                    rec['entity_kind'] = found['kind']
                    rec['entity_id'] = found['id']
                    used_entities_file.write(json.dumps(found,sort_keys=True)+"\n")
                    processed_file.write(json.dumps(rec,sort_keys=True)+"\n")
        logging.debug("matched %d entities" % matches)