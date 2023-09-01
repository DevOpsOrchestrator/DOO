WITH_LOOP = ["with_list","with_items","with_indexed_items","with_flattened","with_together","with_dict",
             "with_sequence","with_subelements","with_random_choice"]

COMMOM_ATTRIBUTES = ["name", "vars","loop","when","any_errors_fatal","check_mode","collections", "connection", 
                     "debugger", "delegate_facts", "diff", "environment","ignore_errors", "ignore_unreachable",
                     "module_defaults", "no_log","port", "remote_user", "run_once", "tags", "throttle", "timeout"]

BECOME_ATTRIBUTES = ["become","become_exe","become_flags", "become_method","become_user"]

ATTRIBUTES_TASK = ["action", "args","async","changed_when","delegate_to","failed_when","local_action","loop_control","module_defaults",
                   "register", "until","notify"] + BECOME_ATTRIBUTES + COMMOM_ATTRIBUTES + WITH_LOOP

ATTRIBUTES_PLAYBOOK = ["fact_path", "force_handlers", "gather_facts", "gather_subset","gather_timeout", "handlers", 
                       "hosts", "max_fail_percentage", "order", "post_tasks", "pre_tasks", "roles", "serial", 
                       "tasks", "vars_files", "vault_identity", "vault_password_file"] + BECOME_ATTRIBUTES + COMMOM_ATTRIBUTES + WITH_LOOP

ATTRIBUTES_ROLE = [ "delegate_to"] + BECOME_ATTRIBUTES + COMMOM_ATTRIBUTES + WITH_LOOP





