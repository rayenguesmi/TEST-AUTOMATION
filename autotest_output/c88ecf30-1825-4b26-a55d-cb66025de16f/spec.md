📄 Projet : Demoblaze – Module Electronics

URL : https://www.demoblaze.com/

🛍️ Feature F-001 : Affichage des produits Electronics

L'utilisateur peut visualiser la liste des produits électroniques disponibles.

Critères d'acceptation :
La page affiche une liste de produits.
Chaque produit contient : nom, prix, image.
Les produits sont cliquables.
Les catégories (Phones, Laptops, Monitors) filtrent les produits.
Flux positif :
Accéder à la page d’accueil.
Cliquer sur une catégorie (ex: Phones).
Visualiser les produits affichés.
Flux négatifs :
Charger la page avec mauvaise URL → erreur ou page vide.
Problème de chargement → produits non affichés.
🔍 Feature F-002 : Navigation vers détail produit

L'utilisateur peut consulter les détails d’un produit.

Critères d'acceptation :
Redirection vers la page produit après clic.
Affichage : nom, description, prix.
Présence du bouton "Add to cart".
Flux positif :
Cliquer sur un produit.
Accéder à sa page détail.
Flux négatifs :
Cliquer sur un produit inexistant → erreur ou page non trouvée.
Produit non chargé correctement.
🛒 Feature F-003 : Ajout au panier

L'utilisateur peut ajouter un produit au panier.

Critères d'acceptation :
Le produit est ajouté au panier.
Une alerte de confirmation est affichée.
Le panier contient le produit ajouté.
Flux positif :
Cliquer sur "Add to cart".
Confirmer l’ajout.
Flux négatifs :
Ajouter sans connexion (selon comportement du site).
Produit indisponible ou erreur JS.
📊 Feature F-004 : Navigation entre catégories

L'utilisateur peut filtrer les produits par catégorie.

Critères d'acceptation :
Les produits changent selon la catégorie sélectionnée.
Les catégories disponibles :
Phones
Laptops
Monitors
Flux positif :
Cliquer sur une catégorie.
Voir les produits correspondants.
Flux négatifs :
Catégorie invalide → aucun produit affiché.
Mauvais chargement dynamique (AJAX).
📄 Feature F-005 : Navigation (Pagination implicite / chargement dynamique)

L'utilisateur peut parcourir plusieurs produits.

Critères d'acceptation :
Les produits sont chargés dynamiquement.
Navigation fluide sans rechargement complet.
Flux positif :
Naviguer entre différentes catégories.
Voir différents produits apparaître.
Flux négatifs :
Produits non mis à jour.
Problème de chargement AJAX.
🔎 Feature F-006 : Contact utilisateur

L'utilisateur peut envoyer un message via le formulaire contact.

Critères d'acceptation :
Champs disponibles :
Email
Name
Message
Message envoyé avec succès.
Flux positif :
Remplir le formulaire.
Cliquer sur "Send message".
Flux négatifs :
Champs vides → erreur ou blocage.
Email invalide.
🔐 Feature F-007 : Authentification (Login / Sign Up)

L'utilisateur peut créer un compte et se connecter.

Critères d'acceptation :
Création de compte via Sign Up.
Connexion via Login.
Message de succès ou erreur.
Flux positif :
Créer un compte.
Se connecter avec succès.
Flux négatifs :
Mauvais identifiants.
Utilisateur déjà existant.
💳 Feature F-008 : Passage de commande (Checkout)

L'utilisateur peut finaliser un achat.

Critères d'acceptation :
Formulaire affiché :
Name, Country, City
Credit Card, Month, Year
Confirmation de commande affichée.
Flux positif :
Ajouter produit au panier.
Cliquer sur "Place Order".
Remplir formulaire → valider.
Flux négatifs :
Champs vides → erreur.
Données invalides.




