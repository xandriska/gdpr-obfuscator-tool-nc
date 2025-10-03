'''
notes, thoughts, ideas, hopes & dreams:

- tool will take its input (S3 location & field names) and pass to lambda_handler event (maybe using get_file_from_s3?). event can be a JSON object/dict with bucket &
    key names and a list of field names to obfuscate.

- there will be a main obfuscate function that will be called by the lambda_handler. this function will take the event dict as input.

- the obfuscate function will utilise smart_open to read the files directly from s3, apply obfuscation logic to the specified fields 
    and write the obfuscated data back to s3 as a new file. 

- the lambda handler will use the config from event and pass these variables in to the obfuscate function, returning the result ie.

    def lambda_handler(event, context):
    
        cfg = event.get("config") or event
        input_s3 = cfg["input_s3"]
        output_s3 = cfg["output_s3"]
        field_map = cfg.get("fields", {})

        result = obfuscate(input_s3, output_s3, field_map)

        return result




'''