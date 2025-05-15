import json

def tags_from_payload(payload: dict|list, exceptions: list[str] = []) -> dict:
    """This function recursively generates a dict of tags from nested dicts and or lists that contain dicts.
    It will return all tags from all nested dicts with their values, but ignore all list items, that are not dicts.
    i.e. this payload:
        {
            "key1": true,
            "key2": 10.0,
            "key3": [
                {
                    "key1": 5
                }
            ],
            "key4": [10, 11, 12]
        }
    will return this:
        {"key1": true, "key2": 10.0, "key3_key1": 5}

    Args:
        payload (dict | list): Dict or list that contains dicts, that tags are to be taken from.
        exceptions (list[str], optional): A list of keys or tags, that should be excluded from the result. Defaults to [].

    Returns:
        dict: Flattened dict containing all tags from the payload input parameter with their values.
    """    
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