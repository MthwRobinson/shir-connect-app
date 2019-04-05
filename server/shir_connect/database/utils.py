"""Database utility functions."""
import shir_connect.configuration as conf

def build_age_groups():
    """ Builds the SQL case statement to determine a
    participant's age group """
    age_groups = conf.AGE_GROUPS
    sql = ' CASE '
    for group in age_groups:
        # Build the conditions
        conditions = []
        if 'min' in age_groups[group]:
            condition = ' age >= %s '%(age_groups[group]['min'])
            conditions.append(condition)
        if 'max' in age_groups[group]:
            condition = ' age < %s '%(age_groups[group]['max'])
            conditions.append(condition)

        # If there are no conditions, skip thegroup
        if len(conditions) == 0:
            continue
        # Build the SQL statement
        else:
            sql += ' WHEN ' + ' AND '.join(conditions)
            sql += ' THEN ' + " '%s' "%(group)
    sql += " ELSE 'Unknown' END as age_group "
    return sql
