#!/usr/bin/env python
# coding: utf-8


import os
import pandas as pd
import matplotlib.pyplot as plt




def autolabel(rects, axe=None, color=None):
    """Attach a text label above each bar in *rects*, displaying its height."""
    for rect in rects:
        height = rect.get_height()
        axe.annotate('{0}'.format(height),
                     xy=(rect.get_x() + rect.get_width() / 2, height),
                     xytext=(0, 1),  # 3 points vertical offset
                     textcoords="offset points",
                     ha='center', va='bottom',
                     color=color)


def f(row):
    donnee = row.values[0]
    pop    = row.values[1]
    return donnee/pop*10000
    
    
    
def dateRenomme(row):
    return row[8:]+"-"+row[5:7]




class donneesCovid:
    
    def __init__(self):

        self.dossier_principal = os.getcwd()
        self.dossier_donnees   = os.path.join(self.dossier_principal, "donnees")
        self.dossier_app    = os.path.join(self.dossier_principal, "app")
        self.dossier_static    = os.path.join(self.dossier_app, "static")
        self.dossier_res       = os.path.join(self.dossier_static, "res")
        
        # Chargement des données du Covid
        donnees = {}
        dates = []
        heures = []
        donnees_eta = {}
        dates_eta = []
        heures_eta = []

        for fichier in os.listdir(os.path.join(self.dossier_donnees, "covid-19")):
            fnom = fichier.split('.')[0]
        
            if "donnees-hospitalieres-covid19" in fnom:
                fnom = fnom.replace("donnees-hospitalieres-covid19-", "").split("-")
                aammjj = fnom[0] + fnom[1] + fnom[2]
                hhmm = fnom[3][:2] + fnom[3][3:]
                dates.append(aammjj)
                heures.append(hhmm)
                donnees[aammjj] = pd.read_csv(os.path.join(os.path.join(self.dossier_donnees, "covid-19"), fichier), sep=";")
                donnees[aammjj] = donnees[aammjj].dropna()
            
            elif "donnees-hospitalieres-etablissements-covid19" in fnom:
                fnom = fnom.replace("donnees-hospitalieres-etablissements-covid19-", "").split("-")
                aammjj = fnom[0] + fnom[1] + fnom[2]
                hhmm = fnom[3][:2] + fnom[3][3:]
                dates_eta.append(aammjj)
                heures_eta.append(hhmm)
                donnees_eta[aammjj] = pd.read_csv(os.path.join(os.path.join(self.dossier_donnees, "covid-19"), fichier), sep=";")
        


            # Chargement des données de la population française
            for fichier in os.listdir(os.path.join(self.dossier_donnees, "population")):
                fnom = fichier.split('.')[0]
                
                if fnom == "Departements":
                    self.donnees_dep = pd.read_csv(os.path.join(os.path.join(self.dossier_donnees, "population"), fichier), sep=";")
                    self.donnees_dep = self.donnees_dep.drop(['Unnamed: 7'], axis=1)
    
                if fnom == "Regions":
                    self.donnees_reg = pd.read_csv(os.path.join(os.path.join(self.dossier_donnees, "population"), fichier), sep=";")
                    self.donnees_reg["CODREG"] = self.donnees_reg["CODREG"].apply(lambda x: str(x))
                
                if fnom == "departement2020":
                    self.donnees_decoupage = pd.read_csv(os.path.join(os.path.join(self.dossier_donnees, "population"), fichier), sep=",")
                    
            decoupage_reg = {str(i):el for i, el in zip(self.donnees_reg["CODREG"].values, self.donnees_reg["REG"].values)}
            decoupage_dep = {str(i):el for i, el in zip(self.donnees_dep["CODDEP"].values, self.donnees_dep["DEP"].values)}
            self.dep_vers_reg  = {str(i):el for i, el in zip(self.donnees_decoupage["dep"].values, self.donnees_decoupage["reg"].values)}
        
            # Table des infos hospitalière départementales
            self.donnees_etude_dep = donnees[dates[-1]]
            self.donnees_etude_dep["reg"] = self.donnees_etude_dep["dep"].apply(lambda x: str(self.dep_vers_reg[str(x)]))
            
            # Table des infos hospitalière régionnales
            etude = self.donnees_etude_dep.copy()
            etude = etude.drop(["dep"], axis=1)
            etude = etude.reset_index(drop=True)
            self.donnees_etude_reg = pd.DataFrame()
            for jour in etude["jour"].unique():
                for sexe in etude["sexe"].unique():
                    etude_tempo = etude[(etude["jour"]==jour) & (etude["sexe"]==sexe)]
                    etude_tempo = etude_tempo.groupby(['reg'], as_index=False).sum()
                    etude_tempo["jour"] = etude_tempo["reg"].apply(lambda x: jour)
                    etude_tempo["sexe"] = etude_tempo["reg"].apply(lambda x: sexe)
                    self.donnees_etude_reg = pd.concat([self.donnees_etude_reg, etude_tempo])
            del etude, etude_tempo
            
            # Table des infos hospitalière nationnales
            etude = self.donnees_etude_dep.copy()
            etude = etude.drop(["dep", "reg"], axis=1)
            etude = etude.reset_index(drop=True)
            self.donnees_etude_pays = pd.DataFrame()
            for sexe in etude["sexe"].unique():
                etude_tempo = etude[etude["sexe"]==sexe]
                etude_tempo = etude_tempo.groupby(['jour'], as_index=False).sum()
                etude_tempo["sexe"] = etude_tempo["jour"].apply(lambda x: sexe)
                self.donnees_etude_pays = pd.concat([self.donnees_etude_pays, etude_tempo])
            del etude, etude_tempo
            
            # Table des infos de population nationnales
            self.donnees_pays = self.donnees_dep.copy()
            self.donnees_pays["PAYS"] = self.donnees_pays["DEP"].apply(lambda x: "France")
            self.donnees_pays = self.donnees_pays.drop(["DEP", "CODDEP"], axis=1)
            self.donnees_pays = self.donnees_pays.reset_index(drop=True)
            self.donnees_pays = self.donnees_pays.groupby(['PAYS'], as_index=False).sum()
            
            
            
    def departementVersRegion(self, idDep, transformeur=None):
        if transformeur == None:
            transformeur = self.dep_vers_reg
        idReg = str(transformeur[str(idDep)])
        
        return idReg



            
    def nomDepartement(self, idDep, pop=None):
        if pop == None:
            pop = self.donnees_dep.copy()
        pop = pop[pop["CODDEP"]==str(idDep)]
        nomDep = pop["DEP"].values[0]
        
        return nomDep



    def afficheDepartement(self, idDep, etude=None, pop=None, sauvegarde=False):
        if pop == None:
            pop = self.donnees_dep.copy()
        if etude == None:
            etude = self.donnees_etude_dep.copy()
        etude = etude[etude["dep"]==str(idDep)]
        
        # Répartition Hommes / Femmes :
        etude_h = etude[etude["sexe"]==1]
        etude_f = etude[etude["sexe"]==2]
        hosp_h_f = [round(etude_h["hosp"].values[-1] / (etude_f["hosp"].values[-1] + etude_h["hosp"].values[-1]) * 100,2),
                    round(etude_f["hosp"].values[-1] / (etude_f["hosp"].values[-1] + etude_h["hosp"].values[-1]) * 100,2)]
        rad_h_f = [round(etude_h["rad"].values[-1] / (etude_f["rad"].values[-1] + etude_h["rad"].values[-1]) * 100,2),
                   round(etude_f["rad"].values[-1] / (etude_f["rad"].values[-1] + etude_h["rad"].values[-1]) * 100,2)]
        dc_h_f = [round(etude_h["dc"].values[-1] / (etude_f["dc"].values[-1] + etude_h["dc"].values[-1]) * 100,2),
                  round(etude_f["dc"].values[-1] / (etude_f["dc"].values[-1] + etude_h["dc"].values[-1]) * 100,2)]
        # Total des genres (des fois supérieur à la somme H + F)
        etude = etude[etude["sexe"]==0]
        
        # Données de population
        pop = pop[pop["CODDEP"]==str(idDep)]
        nom_dep = pop["DEP"].values[0]
        pop_dep = pop["PTOT"].values[0]
    
        # Renommage des dates
        etude["jour"] = etude["jour"].apply(dateRenomme)
    
        # Initialisation de la figure
        fig = plt.figure(figsize=(2*8,2*5))
    
        # Sous figure 1
        ax1 = fig.add_subplot(2, 2, 1)
        ax1.set_title("État dans les hopitaux")
        b1 = plt.bar(etude["jour"], etude["hosp"], color="C0")
        autolabel(b1, axe=ax1, color="C0")
        b2 = plt.bar(etude["jour"], etude["rea"], color="C3")
        autolabel(b2, axe=ax1, color="w")
        plt.ylabel("Lits occupés")
        plt.xlabel("Dates")
        plt.legend((b1[0], b2[0]), ('Hospitalisations', 'Réanimations'), loc="upper left", fontsize="large")
    
        # Sous figure 2
        ax2 = fig.add_subplot(2, 2, 2, frameon=False)
        msg  =  "Population du département : "
        msg += str(pop_dep)
        plt.text(0.1, 0.8, msg, fontsize="xx-large")
        msg = "Résumé :"
        plt.text(0.1, 0.3, msg, fontsize="xx-large")
        msg  = "Hospitalisations :"
        msg += "\n--> {0} / 10000 habitants".format(round(etude["hosp"].values[-1]/pop_dep*10000, 2))
        msg += "\n--> {0}% H / {1}% F".format(hosp_h_f[0], hosp_h_f[1])
        msg += "\n\n"
        msg += "Guérisons :"
        msg += "\n--> {0} / 10000 habitants".format(round(etude["rad"].values[-1]/pop_dep*10000, 2))
        msg += "\n--> {0}% H / {1}% F".format(rad_h_f[0], rad_h_f[1])
        msg += "\n\n"
        msg += "Décès :"
        msg += "\n--> {0} / 10000 habitants".format(round(etude["dc"].values[-1]/pop_dep*10000, 2))
        msg += "\n--> {0}% H / {1}% F".format(dc_h_f[0], dc_h_f[1])
        plt.text(0.4, 0.0, msg, fontsize="x-large", bbox=dict(facecolor='red', alpha=0.5))
        ax2.get_xaxis().set_visible(False)
        ax2.get_yaxis().set_visible(False)
    
        # Sous figure 3
        ax3 = fig.add_subplot(2, 2, 3)
        ax3.set_title("Guérisons cumulées")
        b3 = plt.bar(etude["jour"], etude["rad"], color="C0")
        plt.ylabel("Personnes")
        plt.xlabel("Dates")
        autolabel(b3, ax3, color="C0")
    
        # Sous figure 4
        ax4 = fig.add_subplot(2, 2, 4)
        ax4.set_title("Décès cumulés")
        b4 = plt.bar(etude["jour"], etude["dc"], color="C0")
        plt.ylabel("Personnes")
        plt.xlabel("Dates")
        autolabel(b4, ax4, color="C0")
        
        fig.suptitle("Données hospitalières pour le département : {0}".format(nom_dep), y=0.035, fontsize="xx-large")
        fig.tight_layout(rect=[0.05, 0.05, 0.95, 0.95])
        
        if sauvegarde:
            plt.savefig(os.path.join(self.dossier_res, "afficheDepartement-{0}".format(idDep)))
            plt.close()
        
    



    def departementVsTous(self, idDep, etude=None, pop=None, sauvegarde=False):
        if pop == None:
            pop = self.donnees_dep.copy()
        if etude == None:
            etude = self.donnees_etude_dep.copy()

        donnees_stat_tot = []
        donnees_stat_dep = []
        for date in etude["jour"].unique():
    
            donnees_pop = etude[etude["sexe"]==0]
            donnees_pop = donnees_pop[donnees_pop["jour"]==date]
            donnees_pop = donnees_pop.drop(columns=["sexe", "jour"])
            donnees_pop = donnees_pop.reset_index(drop=True)
            donnees_pop = donnees_pop.drop([100])
            if len(donnees_pop) > 100:
                donnees_pop = donnees_pop.drop([101])
            donnees_pop["pop"] = pop["PTOT"].values
    
            # Calcule de la part de population
            donnees_pop["stat-hosp"] = donnees_pop[["hosp", "pop"]].apply(f, axis=1)
            donnees_pop["stat-rea"]  = donnees_pop[["rea", "pop"]].apply(f, axis=1)
            donnees_pop["stat-rad"]  = donnees_pop[["rad", "pop"]].apply(f, axis=1)
            donnees_pop["stat-dc"]   = donnees_pop[["dc", "pop"]].apply(f, axis=1)
    
            # Calcule des données statistiques sur tous les départements
            donnees_stat = []
            for col in donnees_pop.columns.values.tolist():
                if "stat" in col:
                    sub_stat = []
                    sub_stat.append(donnees_pop[col].mean())
                    sub_stat.append(donnees_pop[col].std())
                    sub_stat.append(donnees_pop[col].median())
                    sub_stat.append(donnees_pop[col].var())
                    sub_stat.append(donnees_pop[col].min())
                    sub_stat.append(donnees_pop[col].max())
                    donnees_stat.append(sub_stat)
            donnees_stat_tot.append(donnees_stat)

            # Pour le département en question    
            nom_dep = pop[pop["CODDEP"]==str(idDep)]["DEP"].values[0]
            stats = ["stat-hosp", "stat-rea", "stat-rad", "stat-dc"]
            donnees_stat_dep.append([donnees_pop[donnees_pop["dep"]==str(idDep)][stat].values[0] for stat in stats])

    
        # Renommage des dates
        etude["jour"] = etude["jour"].apply(dateRenomme)

        # Initialisation de la figure
        fig = plt.figure(figsize=(2*8,2*5))
    
        titres = ["Nombre d'hospitalisations pour 10000 habitants",
                  "Nombre de réanimations pour 10000 habitants",
                  "Guérisons cumulées pour 10000 habitants",
                  "Décès cumulés pour 10000 habitants"]
        for k in range(len(titres)):
            # Sous figure k
            fig.add_subplot(2, 2, k+1).set_title(titres[k])
            plt.fill_between(etude["jour"].unique(), [el[k][4] for el in donnees_stat_tot], [el[k][5] for el in donnees_stat_tot], label="Min/Max", color="beige")
    #        plt.scatter(etude["jour"].unique(), [el[k][0] for el in donnees_stat_tot], c="C2", marker="*", label="Moyenne des Dep.")
    #        plt.plot(etude["jour"].unique(),    [el[k][0] for el in donnees_stat_tot], c="C2", ls="--")
            plt.scatter(etude["jour"].unique(), [el[k][2] for el in donnees_stat_tot], c="C3", marker="^", label="Médianne des Dep.")
            plt.plot(etude["jour"].unique(),    [el[k][2] for el in donnees_stat_tot], c="C3", ls="--")
            plt.scatter(etude["jour"].unique(), [el[k] for el in donnees_stat_dep], c="black", s=100, label="Département : {0}".format(idDep))
            plt.plot(etude["jour"].unique(),    [el[k] for el in donnees_stat_dep], c="black", linewidth=3)
            plt.legend(loc="upper left")
            plt.ylabel("Cas / 10000 Habitants")
            plt.xlabel("Dates")
        
        fig.suptitle("Comparaison entre les statistiques départementales et le département : {0}".format(nom_dep), y=0.035, fontsize="xx-large")
        fig.tight_layout(rect=[0.05, 0.05, 0.95, 0.95])
        
        if sauvegarde:
            plt.savefig(os.path.join(self.dossier_res, "departementVsTous-{0}".format(idDep)))
            plt.close()
            
            
            
            
            
    def nomRegion(self, idReg, pop=None):
        if pop == None:
            pop = self.donnees_reg.copy()
        pop = pop[pop["CODREG"]==str(idReg)]
        nomReg = pop["REG"].values[0]
        
        return nomReg
        


    def afficheRegion(self, idReg, etude=None, pop=None, sauvegarde=False):
        if pop == None:
            pop = self.donnees_reg.copy()
        if etude == None:
            etude = self.donnees_etude_reg.copy()
        etude = etude[etude["reg"]==str(idReg)]
        
        # Répartition Hommes / Femmes :
        etude_h = etude[etude["sexe"]==1]
        etude_f = etude[etude["sexe"]==2]
        hosp_h_f = [round(etude_h["hosp"].values[-1] / (etude_f["hosp"].values[-1] + etude_h["hosp"].values[-1]) * 100,2),
                    round(etude_f["hosp"].values[-1] / (etude_f["hosp"].values[-1] + etude_h["hosp"].values[-1]) * 100,2)]
        rad_h_f = [round(etude_h["rad"].values[-1] / (etude_f["rad"].values[-1] + etude_h["rad"].values[-1]) * 100,2),
                   round(etude_f["rad"].values[-1] / (etude_f["rad"].values[-1] + etude_h["rad"].values[-1]) * 100,2)]
        dc_h_f = [round(etude_h["dc"].values[-1] / (etude_f["dc"].values[-1] + etude_h["dc"].values[-1]) * 100,2),
                  round(etude_f["dc"].values[-1] / (etude_f["dc"].values[-1] + etude_h["dc"].values[-1]) * 100,2)]
        # Total des genres (des fois supérieur à la somme H + F)
        etude = etude[etude["sexe"]==0]
        
        # Données de population
        pop = pop[pop["CODREG"]==str(idReg)]
        nom_reg = pop["REG"].values[0]
        pop_reg = pop["PTOT"].values[0]
        
        # Renommage des dates
        etude["jour"] = etude["jour"].apply(dateRenomme)
        
        # Initialisation de la figure
        fig = plt.figure(figsize=(2*8,2*5))
    
        # Sous figure 1
        ax1 = fig.add_subplot(2, 2, 1)
        ax1.set_title("État dans les hopitaux")
        b1 = plt.bar(etude["jour"], etude["hosp"], color="C0")
        autolabel(b1, axe=ax1, color="C0")
        b2 = plt.bar(etude["jour"], etude["rea"], color="C3")
        autolabel(b2, axe=ax1, color="w")
        plt.ylabel("Lits occupés")
        plt.xlabel("Dates")
        plt.legend((b1[0], b2[0]), ('Hospitalisations', 'Réanimations'), loc="upper left", fontsize="large")
    
        # Sous figure 2
        ax2 = fig.add_subplot(2, 2, 2, frameon=False)
        msg  =  "Population de la région : "
        msg += str(pop_reg)
        plt.text(0.1, 0.8, msg, fontsize="xx-large")
        msg = "Résumé :"
        plt.text(0.1, 0.3, msg, fontsize="xx-large")
        msg  = "Hospitalisations :"
        msg += "\n--> {0} / 10000 habitants".format(round(etude["hosp"].values[-1]/pop_reg*10000, 2))
        msg += "\n--> {0}% H / {1}% F".format(hosp_h_f[0], hosp_h_f[1])
        msg += "\n\n"
        msg += "Guérisons :"
        msg += "\n--> {0} / 10000 habitants".format(round(etude["rad"].values[-1]/pop_reg*10000, 2))
        msg += "\n--> {0}% H / {1}% F".format(rad_h_f[0], rad_h_f[1])
        msg += "\n\n"
        msg += "Décès :"
        msg += "\n--> {0} / 10000 habitants".format(round(etude["dc"].values[-1]/pop_reg*10000, 2))
        msg += "\n--> {0}% H / {1}% F".format(dc_h_f[0], dc_h_f[1])
        plt.text(0.4, 0.0, msg, fontsize="x-large", bbox=dict(facecolor='red', alpha=0.5))
        ax2.get_xaxis().set_visible(False)
        ax2.get_yaxis().set_visible(False)
    
        # Sous figure 3
        ax3 = fig.add_subplot(2, 2, 3)
        ax3.set_title("Guérisons cumulées")
        b3 = plt.bar(etude["jour"], etude["rad"], color="C0")
        plt.ylabel("Personnes")
        plt.xlabel("Dates")
        autolabel(b3, ax3, color="C0")
    
        # Sous figure 4
        ax4 = fig.add_subplot(2, 2, 4)
        ax4.set_title("Décès cumulés")
        b4 = plt.bar(etude["jour"], etude["dc"], color="C0")
        plt.ylabel("Personnes")
        plt.xlabel("Dates")
        autolabel(b4, ax4, color="C0")
        
        fig.suptitle("Données hospitalières pour la région : {0}".format(nom_reg), y=0.035, fontsize="xx-large")
        fig.tight_layout(rect=[0.05, 0.05, 0.95, 0.95])
        
        if sauvegarde:
            plt.savefig(os.path.join(self.dossier_res, "afficheRegion-{0}".format(idReg)))
            plt.close()



    def regionVsTous(self, idReg, etude=None, pop=None, sauvegarde=False):
        if pop == None:
            pop = self.donnees_reg.copy()
        if etude == None:
            etude = self.donnees_etude_reg.copy()
        donnees_stat_tot = []
        donnees_stat_reg = []
        for date in etude["jour"].unique():
    
            donnees_pop = etude[etude["sexe"]==0]
            donnees_pop = donnees_pop[donnees_pop["jour"]==date]
            donnees_pop = donnees_pop.drop(columns=["sexe", "jour"])
            donnees_pop = donnees_pop.reset_index(drop=True)
            if len(donnees_pop) > 17:
                donnees_pop = donnees_pop.drop([12])
            donnees_pop["pop"] = pop["PTOT"].values
    
            # Calcule de la part de population
            donnees_pop["stat-hosp"] = donnees_pop[["hosp", "pop"]].apply(f, axis=1)
            donnees_pop["stat-rea"]  = donnees_pop[["rea", "pop"]].apply(f, axis=1)
            donnees_pop["stat-rad"]  = donnees_pop[["rad", "pop"]].apply(f, axis=1)
            donnees_pop["stat-dc"]   = donnees_pop[["dc", "pop"]].apply(f, axis=1)
    
            # Calcule des données statistiques sur tous les départements
            donnees_stat = []
            for col in donnees_pop.columns.values.tolist():
                if "stat" in col:
                    sub_stat = []
                    sub_stat.append(donnees_pop[col].mean())
                    sub_stat.append(donnees_pop[col].std())
                    sub_stat.append(donnees_pop[col].median())
                    sub_stat.append(donnees_pop[col].var())
                    sub_stat.append(donnees_pop[col].min())
                    sub_stat.append(donnees_pop[col].max())
                    donnees_stat.append(sub_stat)
            donnees_stat_tot.append(donnees_stat)
    
            # Pour le département en question    
            nom_reg = pop[pop["CODREG"]==str(idReg)]["REG"].values[0]
            stats = ["stat-hosp", "stat-rea", "stat-rad", "stat-dc"]
            donnees_stat_reg.append([donnees_pop[donnees_pop["reg"]==str(idReg)][stat].values[0] for stat in stats])
    
        
        # Renommage des dates
        etude["jour"] = etude["jour"].apply(dateRenomme)
    
        # Initialisation de la figure
        fig = plt.figure(figsize=(2*8,2*5))
    
        titres = ["Nombre d'hospitalisations pour 10000 habitants",
                  "Nombre de réanimations pour 10000 habitants",
                  "Guérisons cumulées pour 10000 habitants",
                  "Décès cumulés pour 10000 habitants"]
        for k in range(len(titres)):
            # Sous figure k
            fig.add_subplot(2, 2, k+1).set_title(titres[k])
            plt.fill_between(etude["jour"].unique(), [el[k][4] for el in donnees_stat_tot], [el[k][5] for el in donnees_stat_tot], label="Min/Max", color="beige")
            plt.scatter(etude["jour"].unique(), [el[k][2] for el in donnees_stat_tot], c="C3", marker="^", label="Médianne des Dep.")
            plt.plot(etude["jour"].unique(),    [el[k][2] for el in donnees_stat_tot], c="C3", ls="--")
            plt.scatter(etude["jour"].unique(), [el[k] for el in donnees_stat_reg], c="black", s=100, label="Région : {0}".format(idReg))
            plt.plot(etude["jour"].unique(),    [el[k] for el in donnees_stat_reg], c="black", linewidth=3)
            plt.legend(loc="upper left")
            plt.ylabel("Cas / 10000 Habitants")
            plt.xlabel("Dates")
        
        fig.suptitle("Comparaison entre les statistiques régionales et la région : {0}".format(nom_reg), y=0.035, fontsize="xx-large")
        fig.tight_layout(rect=[0.05, 0.05, 0.95, 0.95])
        
        if sauvegarde:
            plt.savefig(os.path.join(self.dossier_res, "regionVsTous-{0}".format(idReg)))
            plt.close()




    def nomPays(self, pop=None):
        if pop == None:
            pop = self.donnees_pays.copy()
        nomPays = "France"
        
        return nomPays
    


    def affichePays(self, etude=None, pop=None, sauvegarde=False):
        if pop == None:
            pop = self.donnees_pays.copy()
        if etude == None:
            etude = self.donnees_etude_pays.copy()
        
        # Répartition Hommes / Femmes :
        etude_h = etude[etude["sexe"]==1]
        etude_f = etude[etude["sexe"]==2]
        hosp_h_f = [round(etude_h["hosp"].values[-1] / (etude_f["hosp"].values[-1] + etude_h["hosp"].values[-1]) * 100,2),
                    round(etude_f["hosp"].values[-1] / (etude_f["hosp"].values[-1] + etude_h["hosp"].values[-1]) * 100,2)]
        rad_h_f = [round(etude_h["rad"].values[-1] / (etude_f["rad"].values[-1] + etude_h["rad"].values[-1]) * 100,2),
                   round(etude_f["rad"].values[-1] / (etude_f["rad"].values[-1] + etude_h["rad"].values[-1]) * 100,2)]
        dc_h_f = [round(etude_h["dc"].values[-1] / (etude_f["dc"].values[-1] + etude_h["dc"].values[-1]) * 100,2),
                  round(etude_f["dc"].values[-1] / (etude_f["dc"].values[-1] + etude_h["dc"].values[-1]) * 100,2)]
        # Total des genres (des fois supérieur à la somme H + F)
        etude = etude[etude["sexe"]==0]
        
        # Données de population
        nom_pays = "France"
        pop_pays = pop["PTOT"].values[0]
        
        # Renommage des dates
        etude["jour"] = etude["jour"].apply(dateRenomme)
        
        # Initialisation de la figure
        fig = plt.figure(figsize=(2*8,2*5))
    
        # Sous figure 1
        ax1 = fig.add_subplot(2, 2, 1)
        ax1.set_title("État dans les hopitaux")
        b1 = plt.bar(etude["jour"], etude["hosp"], color="C0")
        autolabel(b1, axe=ax1, color="C0")
        b2 = plt.bar(etude["jour"], etude["rea"], color="C3")
        autolabel(b2, axe=ax1, color="w")
        plt.ylabel("Lits occupés")
        plt.xlabel("Dates")
        plt.legend((b1[0], b2[0]), ('Hospitalisations', 'Réanimations'), loc="upper left", fontsize="large")
    
        # Sous figure 2
        ax2 = fig.add_subplot(2, 2, 2, frameon=False)
        msg  =  "Population du pays : "
        msg += str(pop_pays)
        plt.text(0.1, 0.8, msg, fontsize="xx-large")
        msg = "Résumé :"
        plt.text(0.1, 0.3, msg, fontsize="xx-large")
        msg  = "Hospitalisations :"
        msg += "\n--> {0} / 10000 habitants".format(round(etude["hosp"].values[-1]/pop_pays*10000, 2))
        msg += "\n--> {0}% H / {1}% F".format(hosp_h_f[0], hosp_h_f[1])
        msg += "\n\n"
        msg += "Guérisons :"
        msg += "\n--> {0} / 10000 habitants".format(round(etude["rad"].values[-1]/pop_pays*10000, 2))
        msg += "\n--> {0}% H / {1}% F".format(rad_h_f[0], rad_h_f[1])
        msg += "\n\n"
        msg += "Décès :"
        msg += "\n--> {0} / 10000 habitants".format(round(etude["dc"].values[-1]/pop_pays*10000, 2))
        msg += "\n--> {0}% H / {1}% F".format(dc_h_f[0], dc_h_f[1])
        plt.text(0.4, 0.0, msg, fontsize="x-large", bbox=dict(facecolor='red', alpha=0.5))
        ax2.get_xaxis().set_visible(False)
        ax2.get_yaxis().set_visible(False)
    
        # Sous figure 3
        ax3 = fig.add_subplot(2, 2, 3)
        ax3.set_title("Guérisons cumulées")
        b3 = plt.bar(etude["jour"], etude["rad"], color="C0")
        plt.ylabel("Personnes")
        plt.xlabel("Dates")
        autolabel(b3, ax3, color="C0")
    
        # Sous figure 4
        ax4 = fig.add_subplot(2, 2, 4)
        ax4.set_title("Décès cumulés")
        b4 = plt.bar(etude["jour"], etude["dc"], color="C0")
        plt.ylabel("Personnes")
        plt.xlabel("Dates")
        autolabel(b4, ax4, color="C0")
        
        fig.suptitle("Données hospitalières pour le pays : {0}".format(nom_pays), y=0.035, fontsize="xx-large")
        fig.tight_layout(rect=[0.05, 0.05, 0.95, 0.95])
        
        if sauvegarde:
            plt.savefig(os.path.join(self.dossier_res, "affichePays"))
            plt.close()
        




if __name__ == '__main__':

    covid = donneesCovid()
    
    idDep = 75
    covid.afficheDepartement(idDep, sauvegarde=True)
    covid.departementVsTous(idDep, sauvegarde=True)
    
    idReg = 11
    covid.afficheRegion(idReg, sauvegarde=True)
    covid.regionVsTous(idReg, sauvegarde=True)
    
    covid.affichePays(sauvegarde=True)

