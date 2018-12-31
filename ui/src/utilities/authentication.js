function clearToken() {
  // Clears the JWT from local storate
  localStorage.removeItem('trsToken');
}

export { clearToken };
