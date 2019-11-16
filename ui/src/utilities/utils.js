// Utility functions that are used across components

function getConfig() {
  // Reads in the configuration file name from the REACT_APP_SHIR_CONNECT_CONFIG
  // environmental variable
  return process.env.REACT_APP_SHIR_CONNECT_CONFIG
}
export { getConfig }

function sortByKey(arr, key, ascending=true) {
  // Sorts and array of objects by the specified key
  //
  // Parameters
  // ----------
  // arr: an array of objects
  // key: the key to sort on
  // ascending: sorts ascending if true, descending if false
  //
  // Returns
  // -------
  // the sorted array
  //
  function keySorter(obj1, obj2) {
    let a = obj1[key];
    let b = obj2[key];
    // strip whitespace because it's annoying for sorting
    if(typeof a === 'string'){
      a = a.trim();
    }
    if(typeof b === 'string'){
      b = b.trim();
    }

    // equal items sort equally
    if (a === b) {
      return 0;
    }
    // nulls sort after anything else
    else if (a === null) {
      return 1;
    }
    else if (b === null) {
      return -1;
    }
    // otherwise, if we're ascending, lowest sorts first
    else if (ascending) {
      return a < b ? -1 : 1;
    }
    // if descending, highest sorts first
    else {
      return a < b ? 1 : -1;
    }
  }
  return arr.sort(keySorter);
}
export { sortByKey };
