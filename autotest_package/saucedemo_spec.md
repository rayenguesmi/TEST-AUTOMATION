📄 Projet : Swag Labs – SauceDemo
URL : https://www.saucedemo.com/

🔐 Feature F-001 : Connexion utilisateur
L'utilisateur peut se connecter avec un compte valide.

Critères d'acceptation :
- La redirection vers /inventory.html est effectuée après login.

Flux positif :
1. Accéder à https://www.saucedemo.com/
2. Saisir l'utilisateur "standard_user"
3. Saisir le mot de passe "secret_sauce"
4. Cliquer sur le bouton Login.

🛒 Feature F-002 : Ajout au panier (Après connexion)
L'utilisateur peut ajouter un produit au panier une fois connecté.

Critères d'acceptation :
- Le panier affiche "1" après l'ajout.

Flux positif :
1. SE CONNECTER d'abord avec "standard_user" et "secret_sauce" sur https://www.saucedemo.com/
2. Cliquer sur le bouton "Add to cart" du premier produit affiché (ex: Sauce Labs Backpack).
3. Vérifier que le badge du panier (shopping_cart_badge) contient le texte "1".
