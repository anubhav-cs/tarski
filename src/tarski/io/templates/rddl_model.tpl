domain {domain_name} {{

    requirements = {{ {req_list} }};

    types = {{
{type_list}
    }};

    pvariables = {{
{pvar_list}
    }};

    cpfs {{
{cpfs_list}
    }};

    reward = {reward_expr};

    action-preconditions {{
{action_precondition_list}
    }};

    state-constraints {{
{state_constraint_list}
    }};

    state-invariants {{
{state_invariant_list}
    }};

}}

non-fluents {domain_non_fluents} {{
    domain = {domain_name};

    objects {{
{object_list}
    }};

    non-fluents {{
{non_fluent_expr}
    }};
}}

instance {instance_name} {{

    domain = {domain_name};
    non-fluents = {non_fluents_ref};

    init-state {{
{init_state_fluent_expr}
    }};

    max-non-def-actions = {max_nondef_actions};
    horizon = {horizon};
    discount = {discount};
}}
