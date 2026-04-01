📄 Projet : Demo Web Shop – Module Electronics

URL : https://demowebshop.tricentis.com/electronics

🛍️ Feature F-001 : Affichage des produits Electronics

L'utilisateur peut visualiser la liste des produits électroniques disponibles.

Critères d'acceptation :

La page affiche une liste de produits électroniques.
Chaque produit contient : nom, prix, image.
Les produits sont cliquables.

Flux positif :

Accéder à la page Electronics.
Visualiser la liste des produits.
Cliquer sur un produit.

Flux négatifs :

Charger la page avec mauvaise URL → erreur ou redirection.

🔍 Feature F-002 : Navigation vers détail produit

L'utilisateur peut consulter les détails d’un produit.

Critères d'acceptation :

Redirection vers page produit après clic.
Affichage : description, prix, bouton "Add to cart".

Flux positif :

Cliquer sur un produit.

Flux négatifs :

Cliquer sur un produit indisponible.

🛒 Feature F-003 : Ajout au panier

L'utilisateur peut ajouter un produit électronique au panier.

Critères d'acceptation :

Le produit est ajouté au panier.
Un message de confirmation est affiché.
Le compteur du panier est mis à jour.

Flux positif :

Cliquer sur "Add to cart".

Flux négatifs :

Ajouter un produit en rupture de stock.

📊 Feature F-004 : Filtrage / Tri des produits

L'utilisateur peut trier les produits.

Critères d'acceptation :

Tri par prix (ascendant / descendant).
Tri par nom.
Mise à jour dynamique de la liste.

Flux positif :

Sélectionner une option de tri.

Flux négatifs :

Choisir une option invalide.

📄 Feature F-005 : Pagination

L'utilisateur peut naviguer entre les pages produits.

Critères d'acceptation :

Boutons "Next" et "Previous" fonctionnels.
Les produits changent selon la page.

Flux positif :

Cliquer sur "Next".

Flux négatifs :

Accéder à une page inexistante.

🔎 Feature F-006 : Recherche produit (globale liée)

L'utilisateur peut rechercher un produit électronique.

Critères d'acceptation :

Les résultats correspondent au mot-clé.
Si aucun résultat → message affiché.

Flux positif :

Rechercher "phone" ou "camera".

Flux négatifs :

Rechercher un produit inexistant.
