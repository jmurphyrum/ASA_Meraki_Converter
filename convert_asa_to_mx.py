import re

def convert_asa_to_mx(asa_config):
    mx_rules = []
    object_groups = {}

    # Read ASA configuration file
    with open(asa_config, 'r') as file:
        lines = file.readlines()

    # Process each line in the ASA configuration
    for line in lines:
        line = line.strip()

        # Ignore comments and empty lines
        if not line or line.startswith('!') or line.startswith('#'):
            continue

        # Extract object-group information
        if line.startswith('object-group'):
            object_group_name = re.search(r'object-group (\w+)', line).group(1)
            object_group_type = re.search(r'network|service', line).group(0)
            object_groups[object_group_name] = {'type': object_group_type, 'members': []}
            continue

        # Extract network objects
        if line.startswith('object network'):
            object_name = re.search(r'object network (\w+)', line).group(1)
            object_ip = re.search(r'host (\S+)', line).group(1)
            object_groups[object_name] = {'type': 'network', 'members': [object_ip]}
            continue

        # Extract service objects
        if line.startswith('object service'):
            object_name = re.search(r'object service (\w+)', line).group(1)
            object_protocol = re.search(r'service (\S+)', line).group(1)
            object_port = re.search(r'eq (\S+)', line).group(1)
            object_groups[object_name] = {'type': 'service', 'members': [object_protocol, object_port]}
            continue

        # Process access-list entries
        if line.startswith('access-list'):
            acl_entries = line.split()

            acl_num = acl_entries[1]
            acl_action = acl_entries[2]
            acl_protocol = acl_entries[3]
            acl_source = acl_entries[4]
            acl_dest = acl_entries[5]

            if acl_source in object_groups:
                acl_source = object_groups[acl_source]
            if acl_dest in object_groups:
                acl_dest = object_groups[acl_dest]

            mx_rule = f"{acl_num}: {acl_action}, {acl_protocol}, {acl_source}, {acl_dest}"
            mx_rules.append(mx_rule)

    return mx_rules

# Example usage
asa_config_file = "asa_config.txt"
converted_rules = convert_asa_to_mx(asa_config_file)

# Print the converted Meraki MX rules
for rule in converted_rules:
    print(rule)
