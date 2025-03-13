async function signOut() {
  const { error } = await supabase.auth.signOut();
  if (error) {
    console.error('Erreur de déconnexion:', error.message);
  } else {
    console.log('Déconnexion réussie');
  }
}
