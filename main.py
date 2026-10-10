import os
import json
import sqlite3
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle, RoundedRectangle
from plyer import gps

FICHIER_PROFIL = "profil_utilisateur.json"

# --- UTILITAIRES DE DESIGN ---
class BarreNavigation(BoxLayout):
    def __init__(self, **kwargs):
        super(BarreNavigation, self).__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = 60
        with self.canvas.before:
            Color(1, 1, 1, 1) # Fond blanc de la barre
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(pos=self.update_rect, size=self.update_rect)
        
        # BOUTON ACCUEIL (Emmène vers l'écran d'alerte principal)
        btn_accueil = Button(text="Accueil", background_color=(0,0,0,0), color=(0.1, 0.2, 0.4, 1), bold=True)
        btn_accueil.bind(on_press=lambda x: self.changer_ecran('alerte'))
        self.add_widget(btn_accueil)
        
        # BOUTON CARTE
        btn_carte = Button(text="Carte", background_color=(0,0,0,0), color=(0.5, 0.5, 0.5, 1))
        btn_carte.bind(on_press=lambda x: self.changer_ecran('carte'))
        self.add_widget(btn_carte)
        
        # BOUTON ALERTES (Historique)
        btn_alertes = Button(text="Alertes", background_color=(0,0,0,0), color=(0.5, 0.5, 0.5, 1))
        btn_alertes.bind(on_press=lambda x: self.changer_ecran('historique'))
        self.add_widget(btn_alertes)
        
        # BOUTON SIGNALER
        btn_signaler = Button(text="Signaler", background_color=(0,0,0,0), color=(0.5, 0.5, 0.5, 1))
        btn_signaler.bind(on_press=lambda x: self.changer_ecran('signaler'))
        self.add_widget(btn_signaler)
        
        # BOUTON PROFIL (Emmène vers l'écran de connexion/modification)
        btn_profil = Button(text="Profil", background_color=(0,0,0,0), color=(0.5, 0.5, 0.5, 1))
        btn_profil.bind(on_press=lambda x: self.changer_ecran('connexion'))
        self.add_widget(btn_profil)

    def update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    # Fonction magique qui permet de changer d'écran depuis la barre de navigation
    def changer_ecran(self, nom_ecran):
        app = App.get_running_app()
        app.root.current = nom_ecran

# --- ECRAN 1 : CONNEXION (Sert aussi pour le PROFIL) ---
class EcranConnexion(Screen):
    def __init__(self, **kwargs):
        super(EcranConnexion, self).__init__(**kwargs)
        
        with self.canvas.before:
            Color(0.95, 0.95, 0.96, 1)
            self.bg = Rectangle(size=self.size, pos=self.pos)
        self.bind(pos=self.update_bg, size=self.update_bg)

        layout_principal = BoxLayout(orientation='vertical')
        
        entete = BoxLayout(orientation='vertical', size_hint_y=None, height=80)
        with entete.canvas.before:
            Color(0.05, 0.15, 0.3, 1)
            self.rect_entete = Rectangle(size=entete.size, pos=entete.pos)
        entete.bind(pos=self.update_rect_entete, size=self.update_rect_entete)
        entete.add_widget(Label(text="[b]SECURITE & ALERTE[/b]", markup=True, font_size=20, color=(1, 1, 1, 1)))
        layout_principal.add_widget(entete)

        layout_principal.add_widget(Label(text="[b]Mon Profil / Connexion[/b]", 
                                          markup=True, color=(0, 0, 0, 1), font_size=18, halign="center", 
                                          size_hint_y=None, height=80))

        zone_formulaire = AnchorLayout(anchor_x='center', anchor_y='top')
        carte_blanche = BoxLayout(orientation='vertical', padding=20, spacing=15, size_hint=(0.9, None), height=300)
        with carte_blanche.canvas.before:
            Color(1, 1, 1, 1)
            self.rect_carte = RoundedRectangle(size=carte_blanche.size, pos=carte_blanche.pos, radius=[15])
        carte_blanche.bind(pos=self.update_rect_carte, size=self.update_rect_carte)

        self.input_nom = TextInput(hint_text="Nom complet ou Telephone", multiline=False, size_hint_y=None, height=45, background_color=(0.96, 0.96, 0.96, 1))
        carte_blanche.add_widget(self.input_nom)

        self.input_lieu = TextInput(hint_text="Votre Quartier et Avenue", multiline=False, size_hint_y=None, height=45, background_color=(0.96, 0.96, 0.96, 1))
        carte_blanche.add_widget(self.input_lieu)

        btn_connecter = Button(text="ENREGISTRER / CONNECTER", background_normal='', background_color=(0.85, 0.05, 0.05, 1), 
                               font_size=16, bold=True, size_hint_y=None, height=50)
        btn_connecter.bind(on_press=self.sauvegarder_profil)
        carte_blanche.add_widget(btn_connecter)
        
        carte_blanche.add_widget(Label(text="Remplissez vos informations", color=(0.5, 0.5, 0.5, 1), size_hint_y=None, height=30))

        zone_formulaire.add_widget(carte_blanche)
        layout_principal.add_widget(zone_formulaire)
        layout_principal.add_widget(BarreNavigation())
        
        self.add_widget(layout_principal)

    def update_bg(self, instance, value):
        self.bg.pos = instance.pos
        self.bg.size = instance.size

    def update_rect_entete(self, instance, value):
        self.rect_entete.pos = instance.pos
        self.rect_entete.size = instance.size

    def update_rect_carte(self, instance, value):
        self.rect_carte.pos = instance.pos
        self.rect_carte.size = instance.size

    def on_pre_enter(self, *args):
        if os.path.exists(FICHIER_PROFIL):
            try:
                with open(FICHIER_PROFIL, "r") as f:
                    profil = json.load(f)
                    self.input_nom.text = profil.get("nom", "")
                    self.input_lieu.text = profil.get("lieu", "")
            except Exception:
                pass

    def sauvegarder_profil(self, instance):
        if self.input_nom.text and self.input_lieu.text:
            profil = {
                "nom": self.input_nom.text,
                "lieu": self.input_lieu.text
            }
            with open(FICHIER_PROFIL, "w") as f:
                json.dump(profil, f)
            self.manager.current = 'alerte'

# --- ECRAN 2 : ACCUEIL / ALERTE RAPIDE ---
class EcranAlerte(Screen):
    def __init__(self, **kwargs):
        super(EcranAlerte, self).__init__(**kwargs)
        
        with self.canvas.before:
            Color(0.05, 0.08, 0.12, 1)
            self.bg = Rectangle(size=self.size, pos=self.pos)
        self.bind(pos=self.update_bg, size=self.update_bg)

        self.latitude = 0.0
        self.longitude = 0.0
        self.gps_actif = False

        try:
            gps.configure(on_location=self.sauvegarder_position)
            gps.start(minTime=1000, minDistance=1)
            self.gps_actif = True
        except Exception: 
            self.gps_actif = False

        layout_principal = BoxLayout(orientation='vertical')

        entete = BoxLayout(orientation='horizontal', size_hint_y=None, height=60)
        with entete.canvas.before:
            Color(0.85, 0.05, 0.05, 1)
            self.rect_entete = Rectangle(size=entete.size, pos=entete.pos)
        entete.bind(pos=self.update_rect_entete, size=self.update_rect_entete)
        
        btn_retour = Button(text="< Retour", size_hint_x=None, width=80, 
                            background_color=(0,0,0,0), color=(1, 1, 1, 1), bold=True)
        btn_retour.bind(on_press=self.retour_profil)
        entete.add_widget(btn_retour)

        entete.add_widget(Label(text="[b]DÉCLENCHER UNE ALERTE[/b]", markup=True, font_size=18, color=(1, 1, 1, 1)))
        entete.add_widget(Label(size_hint_x=None, width=80))

        layout_principal.add_widget(entete)

        zone_boutons = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        btn1 = Button(text="1. INFO : Mouvement", background_normal='', background_color=(0.2, 0.6, 1, 1), size_hint_y=None, height=60)
        btn1.bind(on_press=lambda x: self.declencher(1, btn1))
        zone_boutons.add_widget(btn1)

        btn2 = Button(text="2. SUSPECT : Présence", background_normal='', background_color=(0.8, 0.8, 0, 1), size_hint_y=None, height=60)
        btn2.bind(on_press=lambda x: self.declencher(2, btn2))
        zone_boutons.add_widget(btn2)

        btn3 = Button(text="3. INCIDENT : Intrusion", background_normal='', background_color=(1, 0.5, 0, 1), size_hint_y=None, height=60)
        btn3.bind(on_press=lambda x: self.declencher(3, btn3))
        zone_boutons.add_widget(btn3)

        btn4 = Button(text="4. URGENT : Menace armée", background_normal='', background_color=(0.8, 0.1, 0.1, 1), size_hint_y=None, height=60, bold=True)
        btn4.bind(on_press=lambda x: self.declencher(4, btn4))
        zone_boutons.add_widget(btn4)

        btn5 = Button(text="5. INCURSION : ADF NALU", background_normal='', background_color=(0.4, 0, 0, 1), size_hint_y=None, height=60, bold=True)
        btn5.bind(on_press=lambda x: self.declencher(5, btn5))
        zone_boutons.add_widget(btn5)
        
        layout_principal.add_widget(zone_boutons)
        layout_principal.add_widget(BarreNavigation())
        
        self.add_widget(layout_principal)

    def update_bg(self, instance, value):
        self.bg.pos = instance.pos
        self.bg.size = instance.size

    def update_rect_entete(self, instance, value):
        self.rect_entete.pos = instance.pos
        self.rect_entete.size = instance.size

    def retour_profil(self, instance):
        self.manager.current = 'connexion'

    def sauvegarder_position(self, **kwargs):
        self.latitude = kwargs.get('lat', 0.0)
        self.longitude = kwargs.get('lon', 0.0)

    def declencher(self, code, bouton):
        texte_original = bouton.text
        couleur_originale = bouton.background_color
        bouton.text = "ENVOI EN COURS..."
        bouton.background_color = (0.5, 0.5, 0.5, 1)
        
        Clock.schedule_once(lambda dt: self.envoyer_alerte(code), 0.2)
        Clock.schedule_once(lambda dt: self.restaurer_bouton(bouton, texte_original, couleur_originale), 2)

    def restaurer_bouton(self, bouton, texte, couleur):
        bouton.text = texte
        bouton.background_color = couleur

    def envoyer_alerte(self, code):
        if not self.gps_actif:
            self.latitude = 0.710
            self.longitude = 29.526

        try:
            with open(FICHIER_PROFIL, "r") as f:
                profil = json.load(f)
                lieu_texte = profil.get("lieu", "Inconnu")
        except Exception:
            lieu_texte = "Inconnu"

        try:
            connexion = sqlite3.connect('alertes.db')
            curseur = connexion.cursor()
            curseur.execute('''
                INSERT INTO urgences (quartier, avenue, categorie, latitude, longitude)
                VALUES (?, ?, ?, ?, ?)
            ''', (lieu_texte, "-", code, self.latitude, self.longitude))
            connexion.commit()
            connexion.close()
            print(f"Succes : Alerte envoyee depuis {lieu_texte} !")
        except Exception as e:
            print(f"Erreur DB : {e}")

# --- NOUVEAUX ECRANS (EN ATTENTE DE DEVELOPPEMENT) ---

class EcranCarte(Screen):
    def __init__(self, **kwargs):
        super(EcranCarte, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')
        # Zone centrale
        layout.add_widget(Label(text="[b]CARTE DES INCIDENTS[/b]\n\n(Cette fonctionnalité sera bientôt disponible)", 
                                markup=True, halign='center', color=(1,1,1,1)))
        layout.add_widget(BarreNavigation())
        self.add_widget(layout)

class EcranHistoriqueAlertes(Screen):
    def __init__(self, **kwargs):
        super(EcranHistoriqueAlertes, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(Label(text="[b]HISTORIQUE DES ALERTES[/b]\n\n(Ici s'afficheront les notifications)", 
                                markup=True, halign='center', color=(1,1,1,1)))
        layout.add_widget(BarreNavigation())
        self.add_widget(layout)

class EcranSignaler(Screen):
    def __init__(self, **kwargs):
        super(EcranSignaler, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(Label(text="[b]SIGNALER UN ÉVÉNEMENT[/b]\n\n(Formulaire détaillé à venir)", 
                                markup=True, halign='center', color=(1,1,1,1)))
        layout.add_widget(BarreNavigation())
        self.add_widget(layout)


# --- APPLICATION PRINCIPALE ---
class AlerteOichaApp(App):
    def build(self):
        sm = ScreenManager()
        # On ajoute tous les écrans au gestionnaire
        sm.add_widget(EcranConnexion(name='connexion'))
        sm.add_widget(EcranAlerte(name='alerte'))
        sm.add_widget(EcranCarte(name='carte'))
        sm.add_widget(EcranHistoriqueAlertes(name='historique'))
        sm.add_widget(EcranSignaler(name='signaler'))
        
        return sm

if __name__ == '__main__':
    AlerteOichaApp().run()
