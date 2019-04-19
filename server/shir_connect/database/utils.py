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


def sort_results(results, primary_key, sort_key=None,  reverse=False):
    """Sorts results and ensures 'All' is at the top
    and 'Other' is at the bottom. Assumes there is only one key
    that is 'All' and one key that is 'Other'.

    Parameters
    ----------
    results: list
        a list of dictionaries, where each element has the same keys
    primary_key: str
        the key with the display information
    sort_key: str
        the key to sort on
    reverse: boolean
        the order of the sort

    Returns
    -------
    ordered_results: list
    """
    if not sort_key:
        sort_key = primary_key

    all_ = [] 
    other = []
    to_sort = []
    for result in results:
        if result[primary_key] == 'All':
            all_.append(result)
        elif result[primary_key] in ['Other', 'Unknown']:
            other.append(result)
        else:
            to_sort.append(result)
    to_sort = sorted(to_sort, key=lambda k: k[sort_key], reverse=reverse)
    ordered_results = all_ + to_sort + other
    return ordered_results
