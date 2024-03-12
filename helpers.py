import json
from typing import Optional, Dict, Any, Tuple


def get_data_from_file(file_path: str) -> Dict[Any, Any]:
    with open(file_path, 'r') as file:
        data = file.read()
    return json.loads(data)


def get_id_name_info(entity: Dict[str, Optional[str]]) -> Tuple[Optional[str], Optional[str]]:
    if entity is not None:
        entity_id = entity.get('id')
        entity_name = entity.get('name')
    else:
        entity_id = None
        entity_name = None
    return entity_id, entity_name
