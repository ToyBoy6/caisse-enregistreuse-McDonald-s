import json
import os
import random
import time
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, simpledialog, ttk
import winsound

FICHIER_DONNEES = "caisse_data.json"
FICHIER_SON = "bip.wav"

default_categories = {
    "Boissons": [
        {"nom": "Coca-Cola", "prix": 2.50, "tva": 5.5},
        {"nom": "Café", "prix": 1.80, "tva": 5.5},
    ],
    "Plats": [
        {"nom": "Burger", "prix": 8.50, "tva": 10.0},
        {"nom": "Salade", "prix": 7.00, "tva": 10.0},
    ],
    "Menus": [
        {"nom": "Menu Burger", "prix": 12.00, "tva": 10.0},
    ],
}


def jouer_bip():
  """Joue le fichier audio wav personnalisé pour le bip"""
  if os.path.exists(FICHIER_SON):
    try:
      winsound.PlaySound(
          FICHIER_SON, winsound.SND_FILENAME | winsound.SND_ASYNC
      )
    except Exception:
      pass
  else:
    try:
      winsound.Beep(2000, 300)
    except Exception:
      pass


def charger_donnees():
  if os.path.exists(FICHIER_DONNEES):
    try:
      with open(FICHIER_DONNEES, "r", encoding="utf-8") as f:
        data = json.load(f)
        return (
            data.get("categories", default_categories),
            data.get("historique_ventes", []),
            data.get("commandes_actives", []),
            data.get("compteur_commandes", 1),
        )
    except Exception:
      pass
  return default_categories, [], [], 1


def sauvegarder_donnees():
  data = {
      "categories": categories,
      "historique_ventes": historique_ventes,
      "commandes_actives": commandes_actives,
      "compteur_commandes": compteur_commandes,
  }
  try:
    with open(FICHIER_DONNEES, "w", encoding="utf-8") as f:
      json.dump(data, f, ensure_ascii=False, indent=4)
  except Exception as e:
    print("Erreur de sauvegarde:", e)


(
    categories,
    historique_ventes,
    commandes_actives,
    compteur_commandes,
) = charger_donnees()
panier = []


def calculer_totaux():
  total_ht = 0
  total_tva = 0
  for item in panier:
    prix_ttc = item["prix"]
    tva = item["tva"]
    prix_ht = prix_ttc / (1 + tva / 100)
    montant_tva = prix_ttc - prix_ht
    total_ht += prix_ht
    total_tva += montant_tva

  total_ttc = total_ht + total_tva
  return total_ht, total_tva, total_ttc


def mettre_a_jour_panier():
  listbox_panier.delete(0, tk.END)
  for item in panier:
    listbox_panier.insert(
        tk.END, f"{item['nom']} - {item['prix']:.2f} € (TVA: {item['tva']}%)"
    )

  total_ht, total_tva, total_ttc = calculer_totaux()
  lbl_total.config(
      text=(
          f"Total HT: {total_ht:.2f} €\n"
          f"TVA: {total_tva:.2f} €\n"
          f"Total TTC: {total_ttc:.2f} €"
      )
  )


def ajouter_au_panier(article):
  panier.append(article)
  mettre_a_jour_panier()


def vider_panier():
  panier.clear()
  mettre_a_jour_panier()


def afficher_articles(liste_articles):
  for widget in frame_articles.winfo_children():
    widget.destroy()

  colonne = 0
  ligne = 0
  for article in liste_articles:
    btn = tk.Button(
        frame_articles,
        text=f"{article['nom']}\n{article['prix']:.2f} €",
        width=14,
        height=2,
        bg="#e1f5fe",
        font=("Arial", 10),
        command=lambda a=article: ajouter_au_panier(a),
    )
    btn.grid(row=ligne, column=colonne, padx=5, pady=5, sticky="nsew")
    colonne += 1
    if colonne > 5:
      colonne = 0
      ligne += 1


def afficher_categorie(cat):
  if cat in categories:
    afficher_articles(categories[cat])


def afficher_tout():
  tous_les_articles = []
  for liste in categories.values():
    tous_les_articles.extend(liste)
  afficher_articles(tous_les_articles)


def mettre_a_jour_categories():
  for widget in frame_categories.winfo_children():
    widget.destroy()

  btn_tout = tk.Button(
      frame_categories,
      text="🌟 Tout afficher",
      width=14,
      bg="#ffe082",
      font=("Arial", 10, "bold"),
      command=afficher_tout,
  )
  btn_tout.pack(side=tk.LEFT, padx=5)

  for cat in categories.keys():
    btn = tk.Button(
        frame_categories,
        text=cat,
        width=12,
        bg="#bbdefb",
        font=("Arial", 10),
        command=lambda c=cat: afficher_categorie(c),
    )
    btn.pack(side=tk.LEFT, padx=5)

  afficher_tout()
def ouvrir_gestionnaire():
  win_gest = tk.Toplevel(root)
  win_gest.title("Gestion des Catégories, Articles et Menus")
  win_gest.geometry("620x500")

  tk.Label(
      win_gest, text="Gestion du Catalogue", font=("Arial", 12, "bold")
  ).pack(pady=10)

  frame_list = tk.Frame(win_gest)
  frame_list.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

  listbox_cat = tk.Listbox(frame_list, width=20)
  listbox_cat.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

  listbox_art = tk.Listbox(frame_list, width=35)
  listbox_art.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)

  selected_cat_name = [None]

  def rafraichir_listes():
    listbox_cat.delete(0, tk.END)
    for cat in categories.keys():
      listbox_cat.insert(tk.END, cat)
    rafraichir_articles()

  def rafraichir_articles(event=None):
    listbox_art.delete(0, tk.END)
    sel = listbox_cat.curselection()
    if sel:
      selected_cat_name[0] = listbox_cat.get(sel[0])
    if selected_cat_name[0] and selected_cat_name[0] in categories:
      for art in categories.get(selected_cat_name[0], []):
        listbox_art.insert(
            tk.END,
            f"{art['nom']} - {art['prix']:.2f}€ (TVA: {art['tva']}%)",
        )

  listbox_cat.bind("<<ListboxSelect>>", rafraichir_articles)

  frame_btns = tk.Frame(win_gest, pady=5)
  frame_btns.pack(fill=tk.X)

  def ajouter_cat():
    nom = simpledialog.askstring(
        "Nouvelle catégorie", "Nom de la catégorie :", parent=win_gest
    )
    if nom and nom not in categories:
      categories[nom] = []
      sauvegarder_donnees()
      rafraichir_listes()
      mettre_a_jour_categories()

  def suppr_cat():
    sel = listbox_cat.curselection()
    if sel:
      cat = listbox_cat.get(sel[0])
      del categories[cat]
      selected_cat_name[0] = None
      sauvegarder_donnees()
      rafraichir_listes()
      mettre_a_jour_categories()

  def ajouter_art():
    if not selected_cat_name[0]:
      messagebox.showwarning(
          "Attention",
          "Sélectionnez une catégorie à gauche d'abord.",
          parent=win_gest,
      )
      return
    cat = selected_cat_name[0]
    nom = simpledialog.askstring("Nouvel article / menu", "Nom :", parent=win_gest)
    prix = simpledialog.askfloat("Prix", "Prix TTC (€) :", parent=win_gest)
    tva = simpledialog.askfloat("TVA", "Taux de TVA (%) :", parent=win_gest)
    if nom and prix is not None and tva is not None:
      categories[cat].append({"nom": nom, "prix": prix, "tva": tva})
      sauvegarder_donnees()
      rafraichir_articles()
      mettre_a_jour_categories()

  def modifier_art():
    sel_art = listbox_art.curselection()
    if not selected_cat_name[0] or not sel_art:
      messagebox.showwarning(
          "Attention",
          "Sélectionnez un article à droite à modifier.",
          parent=win_gest,
      )
      return
    cat = selected_cat_name[0]
    idx = sel_art[0]
    art_actuel = categories[cat][idx]

    nouveau_nom = simpledialog.askstring(
        "Modifier le nom",
        "Nom :",
        initialvalue=art_actuel["nom"],
        parent=win_gest,
    )
    nouveau_prix = simpledialog.askfloat(
        "Modifier le prix",
        "Prix TTC (€) :",
        initialvalue=art_actuel["prix"],
        parent=win_gest,
    )
    nouvelle_tva = simpledialog.askfloat(
        "Modifier la TVA",
        "Taux de TVA (%) :",
        initialvalue=art_actuel["tva"],
        parent=win_gest,
    )

    if (
        nouveau_nom
        and nouveau_prix is not None
        and nouvelle_tva is not None
    ):
      categories[cat][idx] = {
          "nom": nouveau_nom,
          "prix": nouveau_prix,
          "tva": nouvelle_tva,
      }
      sauvegarder_donnees()
      rafraichir_articles()
      mettre_a_jour_categories()
      listbox_art.selection_set(idx)

  def deplacer_art(direction):
    sel_art = listbox_art.curselection()
    if not selected_cat_name[0] or not sel_art:
      messagebox.showwarning(
          "Attention",
          "Sélectionnez un article à droite à déplacer.",
          parent=win_gest,
      )
      return
    cat = selected_cat_name[0]
    idx = sel_art[0]
    nouvel_idx = idx + direction

    liste = categories[cat]
    if 0 <= nouvel_idx < len(liste):
      liste[idx], liste[nouvel_idx] = liste[nouvel_idx], liste[idx]
      sauvegarder_donnees()
      rafraichir_articles()
      mettre_a_jour_categories()
      listbox_art.selection_set(nouvel_idx)

  def suppr_art():
    sel_art = listbox_art.curselection()
    if selected_cat_name[0] and sel_art:
      cat = selected_cat_name[0]
      idx = sel_art[0]
      if cat in categories and idx < len(categories[cat]):
        del categories[cat][idx]
        sauvegarder_donnees()
        rafraichir_articles()
        mettre_a_jour_categories()
    else:
      messagebox.showwarning(
          "Attention",
          "Sélectionnez un article à droite à supprimer.",
          parent=win_gest,
      )

  def afficher_cmd_modal():
    win_cmd_box = tk.Toplevel(win_gest)
    win_cmd_box.title("Commande de mise à jour .exe")
    win_cmd_box.geometry("620x140")

    tk.Label(
        win_cmd_box,
        text="Copiez cette commande dans votre terminal :",
        font=("Arial", 9, "bold"),
    ).pack(pady=8)

    cmd_text = "pyinstaller --noconsole --onefile C:\\Users\\LENOVO\\AppData\\Local\\Programs\\Python\\Python313\\caisse.py"
    entry_cmd = tk.Entry(win_cmd_box, font=("Courier", 9), width=75)
    entry_cmd.insert(0, cmd_text)
    entry_cmd.pack(padx=10, pady=2)
    entry_cmd.select_range(0, tk.END)
    entry_cmd.focus()

    tk.Label(
        win_cmd_box,
        text="(Le texte est sélectionné, faites Ctrl+C pour le copier)",
        font=("Arial", 8, "italic"),
        fg="gray",
    ).pack(pady=5)

  tk.Button(
      frame_btns, text="+ Catégorie", command=ajouter_cat, bg="#c8e6c9"
  ).grid(row=0, column=0, padx=3, pady=2)
  tk.Button(
      frame_btns, text="- Catégorie", command=suppr_cat, bg="#ffcdd2"
  ).grid(row=0, column=1, padx=3, pady=2)
  tk.Button(
      frame_btns, text="+ Article", command=ajouter_art, bg="#bbdefb"
  ).grid(row=0, column=2, padx=3, pady=2)
  tk.Button(
      frame_btns, text="✏ Modifier", command=modifier_art, bg="#ffe082"
  ).grid(row=0, column=3, padx=3, pady=2)
  tk.Button(
      frame_btns, text="- Article", command=suppr_art, bg="#ffcdd2"
  ).grid(row=0, column=4, padx=3, pady=2)

  frame_deplacement = tk.Frame(win_gest, pady=2)
  frame_deplacement.pack(fill=tk.X)
  tk.Button(
      frame_deplacement,
      text="⬆ Monter",
      command=lambda: deplacer_art(-1),
      bg="#e0e0e0",
      width=15,
  ).pack(side=tk.LEFT, padx=25)
  tk.Button(
      frame_deplacement,
      text="⬇ Descendre",
      command=lambda: deplacer_art(1),
      bg="#e0e0e0",
      width=15,
  ).pack(side=tk.RIGHT, padx=25)

  frame_cmd_btn = tk.Frame(win_gest, pady=5)
  frame_cmd_btn.pack(fill=tk.X)
  tk.Button(
      frame_cmd_btn,
      text="📋 Afficher la commande CMD de MAJ .exe",
      command=afficher_cmd_modal,
      bg="#fff59d",
      font=("Arial", 9, "bold"),
      width=40,
  ).pack(pady=2)

  rafraichir_listes()


def ouvrir_ecran_commandes():
  win_cmd = tk.Toplevel(root)
  win_cmd.title("Suivi des Commandes (Cuisine / Service)")
  win_cmd.geometry("700x450")

  tk.Label(
      win_cmd,
      text="Suivi des Commandes en Temps Réel",
      font=("Arial", 12, "bold"),
  ).pack(pady=10)

  frame_display = tk.Frame(win_cmd)
  frame_display.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

  f_prep = tk.LabelFrame(
      frame_display, text="⏳ En préparation", font=("Arial", 10, "bold")
  )
  f_prep.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
  listbox_prep = tk.Listbox(f_prep, font=("Courier", 9))
  listbox_prep.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

  f_ready = tk.LabelFrame(
      frame_display, text="✅ Prêtes à servir", font=("Arial", 10, "bold")
  )
  f_ready.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)
  listbox_ready = tk.Listbox(f_ready, font=("Courier", 9))
  listbox_ready.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

  def rafraichir_commandes_ui():
    listbox_prep.delete(0, tk.END)
    listbox_ready.delete(0, tk.END)
    for cmd in commandes_actives:
      texte = (
          f"Cmd #{cmd['id']} ({cmd['heure']})\n"
          + "\n".join([f" - {a['nom']}" for a in cmd["articles"]])
          + f"\nTotal: {cmd['total']:.2f}€\n"
          + "-" * 30
      )
      if cmd["statut"] == "preparation":
        listbox_prep.insert(tk.END, texte)
      elif cmd["statut"] == "prete":
        listbox_ready.insert(tk.END, texte)

  def passer_prete():
    sel = listbox_prep.curselection()
    if sel:
      prep_cmds = [c for c in commandes_actives if c["statut"] == "preparation"]
      cmd_a_changer = prep_cmds[sel[0]]
      cmd_a_changer["statut"] = "prete"
      sauvegarder_donnees()
      jouer_bip()
      rafraichir_commandes_ui()

  def archiver_commande():
    sel = listbox_ready.curselection()
    if sel:
      ready_cmds = [c for c in commandes_actives if c["statut"] == "prete"]
      cmd_a_servir = ready_cmds[sel[0]]
      commandes_actives.remove(cmd_a_servir)
      sauvegarder_donnees()
      rafraichir_commandes_ui()

  frame_actions = tk.Frame(win_cmd, pady=10)
  frame_actions.pack(fill=tk.X)

  tk.Button(
      frame_actions,
      text="➡ Marquer comme Prête",
      bg="#fff59d",
      command=passer_prete,
  ).pack(side=tk.LEFT, padx=20)
  tk.Button(
      frame_actions,
      text="✔ Servie / Clôturer",
      bg="#c8e6c9",
      command=archiver_commande,
  ).pack(side=tk.RIGHT, padx=20)

  rafraichir_commandes_ui()


def valider_et_creer_commande(mode_paiement, total_ttc):
  global compteur_commandes
  articles_commande = list(panier)
  heure = datetime.now().strftime("%H:%M:%S")

  commandes_actives.append({
      "id": compteur_commandes,
      "heure": heure,
      "articles": articles_commande,
      "total": total_ttc,
      "statut": "preparation",
  })

  details = [f"{item['nom']} ({item['prix']:.2f}€)" for item in articles_commande]
  historique_ventes.append({
      "id": compteur_commandes,
      "heure": heure,
      "mode": mode_paiement,
      "total": total_ttc,
      "articles": ", ".join(details),
  })

  compteur_commandes += 1
  sauvegarder_donnees()
  jouer_bip()
  vider_panier()


def ouvrir_historique():
  win_hist = tk.Toplevel(root)
  win_hist.title("Historique des Ventes")
  win_hist.geometry("600x400")

  tk.Label(
      win_hist, text="Historique des Transactions", font=("Arial", 12, "bold")
  ).pack(pady=10)

  listbox_hist = tk.Listbox(win_hist, font=("Courier", 9))
  listbox_hist.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

  if not historique_ventes:
    listbox_hist.insert(tk.END, "Aucune transaction enregistrée pour le moment.")
  else:
    for vente in historique_ventes:
      ligne = (
          f"Cmd #{vente['id']} [{vente['heure']}] {vente['mode']} -"
          f" {vente['total']:.2f} € | {vente['articles']}"
      )
      listbox_hist.insert(tk.END, ligne)


def encaisser():
  if not panier:
    messagebox.showwarning("Panier vide", "Le panier est vide.")
    return

  _, _, total_ttc = calculer_totaux()

  win_pay = tk.Toplevel(root)
  win_pay.title("Paiement")
  win_pay.geometry("300x250")

  tk.Label(
      win_pay,
      text=f"Total à payer : {total_ttc:.2f} €",
      font=("Arial", 12, "bold"),
  ).pack(pady=15)
  tk.Label(win_pay, text="Choisissez le mode de paiement :").pack(pady=5)

  def payer_especes():
    win_pay.destroy()

    win_esp = tk.Toplevel(root)
    win_esp.title("Paiement Espèces")
    win_esp.geometry("340x240")

    tk.Label(
        win_esp,
        text=f"Total à payer : {total_ttc:.2f} €",
        font=("Arial", 11, "bold"),
    ).pack(pady=10)

    tk.Label(win_esp, text="Le client a donné (€) :").pack(pady=2)
    entry_donne = tk.Entry(win_esp, font=("Arial", 11), width=12, justify="center")
    entry_donne.pack(pady=5)
    entry_donne.focus()

    lbl_rendu = tk.Label(
        win_esp, text="Je dois rendre : -- €", font=("Arial", 11, "bold"), fg="blue"
    )
    lbl_rendu.pack(pady=5)

    def valider_especes_final():
      try:
        donne = float(entry_donne.get().replace(",", "."))
        if donne < total_ttc:
          messagebox.showerror(
              "Erreur",
              "Le montant donné est inférieur au total !",
              parent=win_esp,
          )
          return
        rendu = donne - total_ttc
        lbl_rendu.config(text=f"Je dois rendre : {rendu:.2f} €", fg="green")

        if messagebox.askyesno(
            "Confirmation",
            f"Le client a donné : {donne:.2f} €\nJe dois rendre :"
            f" {rendu:.2f} €\n\nOK, paiement fini ?",
            parent=win_esp,
        ):
          win_esp.destroy()
          messagebox.showinfo("Paiement", "Paiement en espèces validé !")
          valider_et_creer_commande("Espèces", total_ttc)
      except ValueError:
        messagebox.showerror(
            "Erreur", "Veuillez entrer un montant valide.", parent=win_esp
        )

    tk.Button(
        win_esp,
        text="Ok, paiement fini",
        bg="#a5d6a7",
        font=("Arial", 10, "bold"),
        width=18,
        command=valider_especes_final,
    ).pack(pady=10)

  def payer_cb():
    win_pay.destroy()
    simuler_cb(total_ttc)

  tk.Button(
      win_pay,
      text="💵 Espèces",
      width=20,
      height=2,
      bg="#c8e6c9",
      command=payer_especes,
  ).pack(pady=5)
  tk.Button(
      win_pay,
      text="💳 Carte Bancaire",
      width=20,
      height=2,
      bg="#b3e5fc",
      command=payer_cb,
  ).pack(pady=5)


def simuler_cb(montant):
  win_sim = tk.Toplevel(root)
  win_sim.title("Terminal TPE CB")
  win_sim.geometry("300x180")

  lbl_status = tk.Label(
      win_sim,
      text=f"Montant : {montant:.2f} €\n\nVeuillez insérer ou poser la carte...",
      font=("Arial", 10),
  )
  lbl_status.pack(pady=20)

  root.update()
  time.sleep(1.5)

  lbl_status.config(text="Connexion au centre bancaire...")
  root.update()
  time.sleep(3)

  if random.choice([True, True, True, False]):
    lbl_status.config(
        text="PAIEMENT ACCEPTÉ !", fg="green", font=("Arial", 12, "bold")
    )
    root.update()
    time.sleep(1)
    win_sim.destroy()
    messagebox.showinfo("Succès", "Transaction CB acceptée.")
    valider_et_creer_commande("Carte Bancaire", montant)
  else:
    lbl_status.config(
        text="PAIEMENT REFUSÉ", fg="red", font=("Arial", 12, "bold")
    )
    root.update()
    time.sleep(1)
    win_sim.destroy()
    messagebox.showerror("Échec", "La transaction CB a été refusée. Réessayez.")


root = tk.Tk()
root.title("Logiciel de Caisse Enregistreuse")
root.geometry("850x650")

menu_bar = tk.Menu(root)
admin_menu = tk.Menu(menu_bar, tearoff=0)
admin_menu.add_command(
    label="Gestion Articles / Menus / Catégories", command=ouvrir_gestionnaire
)
admin_menu.add_command(
    label="Suivi des Commandes", command=ouvrir_ecran_commandes
)
admin_menu.add_command(
    label="Historique des Ventes", command=ouvrir_historique
)
menu_bar.add_cascade(label="Paramètres & Gestion", menu=admin_menu)
root.config(menu=menu_bar)

frame_categories = tk.Frame(root, pady=5)
frame_categories.pack(fill=tk.X)

frame_articles = tk.Frame(root, pady=5, height=150)
frame_articles.pack(fill=tk.X, padx=10)

frame_bas = tk.Frame(root, pady=5)
frame_bas.pack(fill=tk.BOTH, expand=True)

listbox_panier = tk.Listbox(frame_bas, width=30, font=("Arial", 10))
listbox_panier.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)

frame_droite = tk.Frame(frame_bas)
frame_droite.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10)

lbl_total = tk.Label(
    frame_droite,
    text="Total HT: 0.00 €\nTVA: 0.00 €\nTotal TTC: 0.00 €",
    font=("Arial", 13, "bold"),
    justify=tk.LEFT,
)
lbl_total.pack(pady=15)

btn_encaisser = tk.Button(
    frame_droite,
    text="💳 ENCAISSER",
    bg="#a5d6a7",
    font=("Arial", 11, "bold"),
    width=18,
    height=2,
    command=encaisser,
)
btn_encaisser.pack(pady=5)

btn_commandes = tk.Button(
    frame_droite,
    text="📋 Suivi Commandes",
    bg="#fff59d",
    width=18,
    command=ouvrir_ecran_commandes,
)
btn_commandes.pack(pady=5)

btn_historique = tk.Button(
    frame_droite,
    text="📜 Historique Ventes",
    bg="#e0e0e0",
    width=18,
    command=ouvrir_historique,
)
btn_historique.pack(pady=5)

btn_vider = tk.Button(
    frame_droite,
    text="Vider le panier",
    bg="#ef9a9a",
    width=18,
    command=vider_panier,
)
btn_vider.pack(pady=5)

mettre_a_jour_categories()

root.mainloop()
