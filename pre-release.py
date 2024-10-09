import requests
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.align import Align
from rich.prompt import Prompt
import os
import requests
import subprocess


console = Console()
layout = Layout()

# Diviser l'écran en trois parties
layout.split(
    Layout(name="header", size=3),
    Layout(ratio=1, name="main"),
)

layout["main"].split_row(
    Layout(name="side"),
    Layout(name="body", ratio=2),
)

# Diviser la section side pour les box en deux
layout["side"].split(Layout(name="side_top"), Layout(name="side_bottom"))

# Ajouter du texte centré dans chaque section
layout["header"].update(Panel(Align.center("Bibliothèque", vertical="middle")))
layout["side_top"].update(Panel(Align.center("• [1] Livre\n• [2] ISBN\n• [3] Auteur\n• [4] Catégorie\n• [5] Images\n• [6] Réinitialiser\n• [7] Retour", vertical="middle")))
layout["side_bottom"].update(Panel(Align.center("Selection :", vertical="middle")))
layout["body"].update(Panel(Align.center("Affichage :", vertical="middle")))

def update_body(info):
    layout["body"].update(Panel(Align.center(info, vertical="middle")))
    console.print(layout)
def update_side_bottom(message):
    layout["side_bottom"].update(Panel(Align.center(message, vertical="middle")))
    console.print(layout)

def search_openlibrary(query_type, query_value):
    base_url = "https://openlibrary.org/search.json"
    params = {query_type: query_value}
    
    try:
        response = requests.get(base_url, params=params)
        data = response.json()

        if data['num_found'] > 0:
            # les premiers résultats
            book = data['docs'][0]
            title = book.get('title', 'Titre non disponible')
            author = ', '.join(book.get('author_name', ['Auteur non disponible']))
            publish_year = book.get('first_publish_year', 'Année de publication non disponible')
            edition_count = book.get('edition_count', 'Nombre d\'éditions non disponible')
            
            # olid
            author_key = book['author_key'][0] if 'author_key' in book and book['author_key'] else None
            cover_id = book.get('cover_i', None)
            
            # url pour lesimages
            global author_image_url
            global book_cover_url
            author_image_url = f"https://covers.openlibrary.org/a/olid/{author_key}-M.jpg" if author_key else "Pas de photo de l'auteur"
            book_cover_url = f"https://covers.openlibrary.org/b/id/{cover_id}-M.jpg" if cover_id else "Pas de couverture disponible"

            info = f"Titre: {title}\nAuteur: {author}\nPremière publication: {publish_year}\nNombre d'éditions: {edition_count}\n\n"
            info += f"Photo de l'auteur : {author_image_url}\n"
            info += f"Couverture du livre : {book_cover_url}\n"
            
            return info
        else:
            return "Aucun résultat trouvé."
    except Exception as e:
        return f"Erreur lors de la requête : {str(e)}"

def get_top_works_by_author(author_name):
    """search : les 5 livres de l'auteur"""
    author_search_url = "https://openlibrary.org/search/authors.json"
    params = {"q": author_name}

    try:
        # Requête pour récupérer l'auteur
        response = requests.get(author_search_url, params=params)
        author_data = response.json()

        if author_data["numFound"] > 0:
            author_key = author_data["docs"][0]["key"]
            author_name = author_data["docs"][0]["name"]

            # Récupérer les oeuvres de l'auteur selectionnéé
            works_url = f"https://openlibrary.org/authors/{author_key}/works.json?limit=5"
            works_response = requests.get(works_url)
            works_data = works_response.json()

            # Afficher les 5 oeivres les plus connues
            top_works = works_data.get("entries", [])[:5]
            works_info = f"Les 5 œuvres les plus connues de {author_name} :\n\n"
            for i, work in enumerate(top_works, start=1):
                title = work.get("title", "Titre non disponible")
                works_info += f"{i}. {title}\n"
            
            return works_info
        else:
            return f"Aucun auteur trouvé pour {author_name}."
    except Exception as e:
        return f"Erreur lors de la requête : {str(e)}"

def get_top_books_by_category(category):
    subject_url = f"https://openlibrary.org/subjects/{category}.json"
    
    try:
        response = requests.get(subject_url)
        subject_data = response.json()
        
        if "works" in subject_data and len(subject_data["works"]) > 0:
            top_books = subject_data["works"][:5]
            category_name = subject_data.get("name", category)
            
            books_info = f"Les 5 livres les plus pertinents dans la catégorie '{category_name}' :\n\n"
            for i, book in enumerate(top_books, start=1):
                title = book.get("title", "Titre non disponible")
                authors = ', '.join([author.get("name", "Auteur non disponible") for author in book.get("authors", [])])
                books_info += f"{i}. {title} par {authors}\n"
            
            return books_info
        else:
            return f"Aucun livre trouvé pour la catégorie {category}."
    except Exception as e:
        return f"Erreur lors de la requête : {str(e)}"

def download_and_open_image(image_url):
    # Obtenir le répertoire de téléchargement par défaut de Windows
    downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")
    
    # Définir le nom du fichier téléchargé
    image_name = image_url.split("/")[-1]  # Prend le dernier segment de l'URL comme nom de fichier
    image_path = os.path.join(downloads_folder, image_name)
    
    # Télécharger l'image
    response = requests.get(image_url)
    
    if response.status_code == 200:
        # Sauvegarder l'image
        with open(image_path, 'wb') as f:
            f.write(response.content)
        #print(f"Image téléchargée avec succès dans : {image_path}")
        
        # Ouvrir l'image avec le visualisateur d'image par défaut
        subprocess.run(['start', image_path], shell=True)
    #else:
     #   print(f"Erreur lors du téléchargement de l'image. Code de réponse : {response.status_code}")

console.print(layout)
book_cover_url = "Pas de couverture disponible"
author_image_url = "Pas de photo de l'auteur"

while True:

    choice = Prompt.ask("Choisissez une option", choices=["1", "2", "3", "4", "5", "6"])

    # choix
    if choice == "1":
        update_side_bottom("Veuillez entrer le nom du livre :")
        book_name = Prompt.ask("Nom du livre")
        if book_name == "7":
            update_body("Affichage :")
            update_side_bottom("Selection :")
        else:
            result = search_openlibrary('title', book_name)
            update_body(result)
    
    elif choice == "2":
        update_side_bottom("Veuillez entrer l'ISBN du livre :")
        isbn = Prompt.ask("ISBN du livre")
        if book_name == "7":
            update_body("Affichage :")
            update_side_bottom("Selection :")
        else:
            result = search_openlibrary('isbn', isbn)
            update_body(result)
    
    elif choice == "3":
        update_side_bottom("Veuillez entrer le nom de l'auteur :")
        author_name = Prompt.ask("Nom de l'auteur")
        if book_name == "7":
            update_body("Affichage :")
            update_side_bottom("Selection :")
        else:
            result = get_top_works_by_author(author_name)
            update_body(result)
    
    elif choice == "4":
        update_side_bottom("Veuillez entrer la catégorie du livre :")
        category = Prompt.ask("Catégorie du livre")
        if book_name == "7":
            update_body("Affichage :")
            update_side_bottom("Selection :")
        else:
            result = get_top_books_by_category(category)
            update_body(result)

    elif choice == "5":
        if not author_image_url == "Pas de photo de l'auteur":
            download_and_open_image(author_image_url)
        if not book_cover_url == "Pas de couverture disponible":
            download_and_open_image(book_cover_url)
        update_body("Affichage :")
        update_side_bottom("Selection :")

    elif choice == "6":
        update_body("Affichage :")
        update_side_bottom("Selection :")