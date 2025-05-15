import json

def tags_from_payload(payload: dict, exceptions: list[str] = []) -> dict:
    
    def tags_recursive(input: dict|list, tag_dict: dict, prev_tag_name: str, exceptions: list[str]):
        prev_tag = prev_tag_name + "_" if prev_tag_name else ""
        if isinstance(input, dict):
            for k, v in input.items():
                if isinstance(v, dict) or isinstance(v, list) and k not in exceptions:
                    tags_recursive(v, tag_dict, prev_tag + k, exceptions)
                else:
                    if k not in exceptions:
                        tag_dict[prev_tag + k] = str(v)
        elif isinstance(input, list):
            for n in range(len(input)):
                if isinstance(input[n], dict) or isinstance(input[n], list):
                    tags_recursive(input[n], tag_dict, prev_tag + str(n), exceptions)
        return
    
    tags = {}
    tags_recursive(payload, tags, "", exceptions)
    
    return tags