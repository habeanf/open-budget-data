import json

if __name__ == "__main__":
    key_fields = sys.argv[1]
    inputs = sys.argv[2:-1]
    output = sys.argv[-1]
    processor = aggregate_jsons_by_key().process(inputs,output,key_fields)

class aggregate_jsons_by_key(object):

    def process(self,inputs,output,key_fields):

        values = {}
        keys = []

        if type(inputs) != list:
            inputs = [inputs]

        for input in inputs:
            for line in file(input):
                line = line.strip()
                data = json.loads(line)
                key = "/".join("%s:%s" % (field,data[field]) for field in key_fields)

                if values.has_key(key):
                    current = values[key]
                    for k,v in data.iteritems():
                        if k not in key_fields and (type(v) == int or type(v) == long):
                            current.setdefault(k,0)
                            current[k]+=v
                        else:
                            current[k] = v
                else:
                    keys.append(key)
                    values[key] = data

        out = file(output,"w")
        for key in keys:
            out.write(json.dumps(values[key],sort_keys=True)+"\n")