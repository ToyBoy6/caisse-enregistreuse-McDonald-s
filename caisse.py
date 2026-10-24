import json
import os
import random
import time
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, simpledialog, ttk

FICHIER_DONNEES = "caisse_data.json"

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
            data.get("plateforme", None),
        )
    except Exception:
      pass
  return default_categories, [], [], 1, None


def sauvegarder_donnees():
  data = {
      "categories": categories,
      "historique_ventes": historique_ventes,
      "commandes_actives": commandes_actives,
      "compteur_commandes": compteur_commandes,
      "plateforme": plateforme_utilisateur,
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
    plateforme_utilisateur,
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
      text=f"Total HT: {total_ht:.2f}€ | TTC: {total_ttc:.2f}€"
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

  max_cols = 3 if plateforme_utilisateur == "Mobile" else 5
  largeur_btn = 10 if plateforme_utilisateur == "Mobile" else 14

  colonne = 0
  ligne = 0
  for article in liste_articles:
    btn = tk.Button(
        frame_articles,
        text=f"{article['nom']}\n{article['prix']:.2f}€",
        width=largeur_btn,
        height=2,
        bg="#e1f5fe",
        font=("Arial", 8),
        command=lambda a=article: ajouter_au_panier(a),
    )
    btn.grid(row=ligne, column=colonne, padx=2, pady=2, sticky="nsew")
    colonne += 1
    if colonne > max_cols:
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
      text="Tout",
      width=8,
      bg="#ffe082",
      font=("Arial", 8, "bold"),
      command=afficher_tout,
  )
  btn_tout.pack(side=tk.LEFT, padx=1)

  for cat in categories.keys():
    btn = tk.Button(
        frame_categories,
        text=cat,
        width=8,
        bg="#bbdefb",
        font=("Arial", 8),
        command=lambda c=cat: afficher_categorie(c),
    )
    btn.pack(side=tk.LEFT, padx=1)

  afficher_tout()
root = tk.Tk()
root.title("Caisse")

if plateforme_utilisateur is None:
  choix = messagebox.askyesno(
      "Configuration", "Utilisez-vous l'application sur un Téléphone / Mobile ?"
  )
  plateforme_utilisateur = "Mobile" if choix else "PC"
  sauvegarder_donnees()

if plateforme_utilisateur == "Mobile":
  root.geometry("400x700")
else:
  root.geometry("850x650")

menu_bar = tk.Menu(root)
admin_menu = tk.Menu(menu_bar, tearoff=0)


def ouvrir_gestionnaire():
  win_gest = tk.Toplevel(root)
  win_gest.title("Gestion Catalogue")
  win_gest.geometry("450x500")

  frame_list = tk.Frame(win_gest)
  frame_list.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

  listbox_cat = tk.Listbox(frame_list, width=14, font=("Arial", 9))
  listbox_cat.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=2)

  listbox_art = tk.Listbox(frame_list, width=22, font=("Arial", 9))
  listbox_art.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=2)

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
            tk.END, f"{art['nom']} - {art['prix']:.2f}€ ({art['tva']}%)"
        )

  listbox_cat.bind("<<ListboxSelect>>", rafraichir_articles)

  def ajouter_cat():
    nom = simpledialog.askstring("Catégorie", "Nom :", parent=win_gest)
    if nom and nom not in categories:
      categories[nom] = []
      sauvegarder_donnees()
      rafraichir_listes()
      mettre_a_jour_categories()

  def suppr_cat():
    sel = listbox_cat.curselection()
    if sel:
      del categories[listbox_cat.get(sel[0])]
      selected_cat_name[0] = None
      sauvegarder_donnees()
      rafraichir_listes()
      mettre_a_jour_categories()

  def ajouter_art():
    if not selected_cat_name[0]:
      messagebox.showwarning(
          "Attention", "Sélectionnez une catégorie.", parent=win_gest
      )
      return
    cat = selected_cat_name[0]
    nom = simpledialog.askstring("Article", "Nom :", parent=win_gest)
    prix = simpledialog.askfloat("Prix", "Prix TTC (€) :", parent=win_gest)
    tva = simpledialog.askfloat("TVA", "TVA % :", parent=win_gest)
    if nom and prix is not None and tva is not None:
      categories[cat].append({"nom": nom, "prix": prix, "tva": tva})
      sauvegarder_donnees()
      rafraichir_articles()
      mettre_a_jour_categories()

  def modifier_art():
    sel_art = listbox_art.curselection()
    if not selected_cat_name[0] or not sel_art:
      messagebox.showwarning(
          "Attention", "Sélectionnez un article.", parent=win_gest
      )
      return
    cat = selected_cat_name[0]
    idx = sel_art[0]
    art = categories[cat][idx]

    n_nom = simpledialog.askstring(
        "Modifier", "Nom :", initialvalue=art["nom"], parent=win_gest
    )
    n_prix = simpledialog.askfloat(
        "Modifier", "Prix :", initialvalue=art["prix"], parent=win_gest
    )
    n_tva = simpledialog.askfloat(
        "Modifier", "TVA % :", initialvalue=art["tva"], parent=win_gest
    )

    if n_nom and n_prix is not None and n_tva is not None:
      categories[cat][idx] = {"nom": n_nom, "prix": n_prix, "tva": n_tva}
      sauvegarder_donnees()
      rafraichir_articles()
      mettre_a_jour_categories()
      listbox_art.selection_set(idx)

  def deplacer_art(direction):
    sel_art = listbox_art.curselection()
    if not selected_cat_name[0] or not sel_art:
      return
    cat = selected_cat_name[0]
    idx = sel_art[0]
    n_idx = idx + direction
    liste = categories[cat]
    if 0 <= n_idx < len(liste):
      liste[idx], liste[n_idx] = liste[n_idx], liste[idx]
      sauvegarder_donnees()
      rafraichir_articles()
      mettre_a_jour_categories()
      listbox_art.selection_set(n_idx)

  def suppr_art():
    sel_art = listbox_art.curselection()
    if selected_cat_name[0] and sel_art:
      cat = selected_cat_name[0]
      idx = sel_art[0]
      if idx < len(categories[cat]):
        del categories[cat][idx]
        sauvegarder_donnees()
        rafraichir_articles()
        mettre_a_jour_categories()

  frame_btns1 = tk.Frame(win_gest, pady=3)
  frame_btns1.pack(fill=tk.X, padx=5)
  tk.Button(
      frame_btns1,
      text="+Cat",
      command=ajouter_cat,
      bg="#c8e6c9",
      font=("Arial", 9),
  ).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=1)
  tk.Button(
      frame_btns1,
      text="-Cat",
      command=suppr_cat,
      bg="#ffcdd2",
      font=("Arial", 9),
  ).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=1)
  tk.Button(
      frame_btns1,
      text="+Art",
      command=ajouter_art,
      bg="#bbdefb",
      font=("Arial", 9),
  ).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=1)
  tk.Button(
      frame_btns1,
      text="Mod",
      command=modifier_art,
      bg="#ffe082",
      font=("Arial", 9),
  ).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=1)
  tk.Button(
      frame_btns1,
      text="-Art",
      command=suppr_art,
      bg="#ffcdd2",
      font=("Arial", 9),
  ).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=1)

  frame_btns2 = tk.Frame(win_gest, pady=3)
  frame_btns2.pack(fill=tk.X, padx=5)
  tk.Button(
      frame_btns2,
      text="⬆ Monter",
      command=lambda: deplacer_art(-1),
      bg="#e0e0e0",
      font=("Arial", 9),
  ).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
  tk.Button(
      frame_btns2,
      text="⬇ Descendre",
      command=lambda: deplacer_art(1),
      bg="#e0e0e0",
      font=("Arial", 9),
  ).pack(side=tk.RIGHT, expand=True, fill=tk.X, padx=2)

  rafraichir_listes()


def ouvrir_ecran_commandes():
  win_cmd = tk.Toplevel(root)
  win_cmd.title("Suivi des Commandes")
  win_cmd.geometry("450x500")

  f_prep = tk.LabelFrame(
      win_cmd, text="⏳ En préparation", font=("Arial", 9, "bold")
  )
  f_prep.pack(fill=tk.BOTH, expand=True, padx=5, pady=3)
  listbox_prep = tk.Listbox(f_prep, font=("Courier", 9))
  listbox_prep.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

  f_ready = tk.LabelFrame(
      win_cmd, text="✅ Prêtes à servir", font=("Arial", 9, "bold")
  )
  f_ready.pack(fill=tk.BOTH, expand=True, padx=5, pady=3)
  listbox_ready = tk.Listbox(f_ready, font=("Courier", 9))
  listbox_ready.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

  def rafraichir_ui():
    listbox_prep.delete(0, tk.END)
    listbox_ready.delete(0, tk.END)
    for cmd in commandes_actives:
      articles_str = ", ".join([a["nom"] for a in cmd["articles"]])
      texte = (
          f"Cmd #{cmd['id']} ({cmd['heure']}) | {cmd['total']:.2f}€\n"
          f"Articles: {articles_str}"
      )
      if cmd["statut"] == "preparation":
        listbox_prep.insert(tk.END, texte)
        listbox_prep.insert(tk.END, "-" * 30)
      elif cmd["statut"] == "prete":
        listbox_ready.insert(tk.END, texte)
        listbox_ready.insert(tk.END, "-" * 30)

  def passer_prete():
    sel = listbox_prep.curselection()
    if sel:
      # Comme on insère des séparateurs, on divise l'index par 2
      idx_reel = sel[0] // 2
      prep = [c for c in commandes_actives if c["statut"] == "preparation"]
      if idx_reel < len(prep):
        prep[idx_reel]["statut"] = "prete"
        sauvegarder_donnees()
        rafraichir_ui()

  def archiver():
    sel = listbox_ready.curselection()
    if sel:
      idx_reel = sel[0] // 2
      ready = [c for c in commandes_actives if c["statut"] == "prete"]
      if idx_reel < len(ready):
        commandes_actives.remove(ready[idx_reel])
        sauvegarder_donnees()
        rafraichir_ui()

  f_btn = tk.Frame(win_cmd, pady=5)
  f_btn.pack(fill=tk.X, padx=5)
  tk.Button(
      f_btn,
      text="➡ Marquer Prête",
      bg="#fff59d",
      font=("Arial", 9, "bold"),
      command=passer_prete,
  ).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
  tk.Button(
      f_btn,
      text="✔ Clôturer / Servie",
      bg="#c8e6c9",
      font=("Arial", 9, "bold"),
      command=archiver,
  ).pack(side=tk.RIGHT, expand=True, fill=tk.X, padx=2)

  rafraichir_ui()


def valider_et_creer_commande(mode, total):
  global compteur_commandes
  commandes_actives.append({
      "id": compteur_commandes,
      "heure": datetime.now().strftime("%H:%M:%S"),
      "articles": list(panier),
      "total": total,
      "statut": "preparation",
  })
  historique_ventes.append({
      "id": compteur_commandes,
      "heure": datetime.now().strftime("%H:%M:%S"),
      "mode": mode,
      "total": total,
      "articles": ", ".join([i["nom"] for i in panier]),
  })
  compteur_commandes += 1
  sauvegarder_donnees()
  vider_panier()


def ouvrir_historique():
  win_hist = tk.Toplevel(root)
  win_hist.title("Historique")
  win_hist.geometry("450x400")
  lb = tk.Listbox(win_hist, font=("Courier", 9))
  lb.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
  if not historique_ventes:
    lb.insert(tk.END, "Aucune vente enregistrée.")
  else:
    for v in historique_ventes:
      lb.insert(
          tk.END,
          f"#{v['id']} [{v['heure']}] {v['mode']} - {v['total']:.2f}€ |"
          f" {v['articles']}",
      )


def encaisser():
  if not panier:
    messagebox.showwarning("Vide", "Panier vide.")
    return
  _, _, total = calculer_totaux()

  win_pay = tk.Toplevel(root)
  win_pay.title("Paiement")
  win_pay.geometry("260x180")

  tk.Label(
      win_pay, text=f"Total : {total:.2f} €", font=("Arial", 11, "bold")
  ).pack(pady=10)

  def especes():
    win_pay.destroy()
    win_esp = tk.Toplevel(root)
    win_esp.title("Espèces")
    win_esp.geometry("260x180")

    tk.Label(win_esp, text=f"Total : {total:.2f} €").pack(pady=5)
    e = tk.Entry(win_esp, justify="center", font=("Arial", 11))
    e.pack(pady=3)
    e.focus()
    lbl_rendu = tk.Label(win_esp, text="Rendu : -- €", fg="blue", font=("Arial", 10, "bold"))
    lbl_rendu.pack(pady=3)

    def valider():
      try:
        donne = float(e.get().replace(",", "."))
        if donne < total:
          return
        rendu = donne - total
        lbl_rendu.config(text=f"Rendu : {rendu:.2f} €", fg="green")
        if messagebox.askyesno("Valider", f"Rendre {rendu:.2f} € ?"):
          win_esp.destroy()
          valider_et_creer_commande("Espèces", total)
      except ValueError:
        pass

    tk.Button(
        win_esp, text="Valider", bg="#a5d6a7", font=("Arial", 9, "bold"), command=valider
    ).pack(pady=5)

  def cb():
    win_pay.destroy()
    win_sim = tk.Toplevel(root)
    win_sim.title("TPE")
    win_sim.geometry("240x130")
    tk.Label(win_sim, text="Paiement CB en cours...", font=("Arial", 10)).pack(pady=20)
    root.update()
    time.sleep(1.5)
    win_sim.destroy()
    valider_et_creer_commande("Carte", total)

  tk.Button(
      win_pay,
      text="💵 Espèces",
      width=16,
      height=2,
      bg="#c8e6c9",
      command=especes,
  ).pack(pady=4)
  tk.Button(
      win_pay,
      text="💳 Carte",
      width=16,
      height=2,
      bg="#b3e5fc",
      command=cb,
  ).pack(pady=4)


admin_menu.add_command(label="Gestion Catalogue", command=ouvrir_gestionnaire)
admin_menu.add_command(label="Suivi Commandes", command=ouvrir_ecran_commandes)
admin_menu.add_command(label="Historique Ventes", command=ouvrir_historique)
menu_bar.add_cascade(label="Paramètres", menu=admin_menu)
root.config(menu=menu_bar)

frame_categories = tk.Frame(root, pady=2)
frame_categories.pack(fill=tk.X, padx=5)

frame_articles = tk.Frame(root, pady=2)
frame_articles.pack(fill=tk.X, padx=5)

listbox_panier = tk.Listbox(root, font=("Arial", 9), height=6)
listbox_panier.pack(fill=tk.BOTH, expand=True, padx=5, pady=3)

lbl_total = tk.Label(
    root, text="Total HT: 0.00€ | TTC: 0.00€", font=("Arial", 10, "bold")
)
lbl_total.pack(pady=2)

frame_actions = tk.Frame(root, pady=3)
frame_actions.pack(fill=tk.X, padx=5)

tk.Button(
    frame_actions,
    text="ENCAISSER",
    bg="#a5d6a7",
    font=("Arial", 9, "bold"),
    command=encaisser,
).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
tk.Button(
    frame_actions,
    text="Cmds",
    bg="#fff59d",
    font=("Arial", 9),
    command=ouvrir_ecran_commandes,
).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
tk.Button(
    frame_actions,
    text="Histo",
    bg="#e0e0e0",
    font=("Arial", 9),
    command=ouvrir_historique,
).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
tk.Button(
    frame_actions,
    text="Vider",
    bg="#ef9a9a",
    font=("Arial", 9),
    command=vider_panier,
).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)

mettre_a_jour_categories()
root.mainloop()
