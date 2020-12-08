
import sqlalchemy 
import pymysql
import pandas as pd
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
from sqlalchemy import create_engine
from jinja2 import Environment, FileSystemLoader 
import hashlib
from datetime import datetime
import plotly.figure_factory as ff
import plotly.graph_objects as go
import plotly.express as px
import plotly
import json
#import extrai_mag_volum_casino as vc
#import CONFIGG
#import flask
from flask import * 

app = Flask(__name__)
#app.config.from_object(Config)

#app.config['SECRET_KEY']='Ma super secret key'

"""app.config.from_object(config)
print(config.CONFIGG['SECRET_KEY'])
capp = app.config['CONFIGG']"""

app.config.update( 
    SECRET_KEY  = 'ma cle secrete'
)

engine = create_engine('mysql+pymysql://simplon:Simplon2020@localhost:3306/perrenot')
con=engine.connect()

@app.route('/', methods=['GET','post'])
def home():
     
    return render_template('pages/index1.html')
#********************************************************************************************************AJOUTER CAMION***************************************************************************
@app.route('/Ajouter_Camion', methods=['GET','post'])
def ajout_camion():
    
    if request.method=='POST':
        Immatriculation=request.form['immatriculation']
        capacite=request.form['capacite']
        type_cam=request.form.getlist('liste_type')
        tonnage=request.form['tonnage']
        fonction=request.form.getlist('liste_fonction')
        assurance=request.form['assurance']
        loyer=request.form['loyer']
        entretient=request.form['entretient']
        pneu=request.form['pneu']
        consommation=request.form['consommation']
        test_matActif=con.execute(text("select camion_mat from camion where camion_mat=:mat_cam and camion_actif=1" ),{'mat_cam':Immatriculation}).fetchone()
        test_matNonActif= con.execute(text("select camion_mat from camion where camion_mat=:mat_cam and camion_actif=0"),{'mat_cam':Immatriculation}).fetchone()
        if test_matActif:
           flash('Ce matricule existe déjà, Veuillez le changer', 'danger')
        elif  test_matNonActif: 
            flash('Ce camion existait déjà a été récupéré', 'success')
            con.execute(text("update camion set camion_actif=1 where camion_mat=:mat_cam and camion_actif=0"),{'mat_cam':Immatriculation})
        else:
            con.execute(text("insert into camion (camion_mat,camion_cap,camion_type,camion_tonnage,camion_fonction, camion_assurance, camion_loyer, camion_entretien, camion_pneus, camion_conso) values(:cam_mat, :cam_cap,:cam_type, :cam_tonnage,:cam_fonc, :cam_assur,:cam_loyer, :cam_entret, :cam_pneu, :cam_cons)"), {'cam_mat':Immatriculation,'cam_cap':capacite, 'cam_type':type_cam[0] , 'cam_tonnage': tonnage ,'cam_fonc':fonction[0] , 'cam_assur': assurance,'cam_loyer': loyer, 'cam_entret': entretient, 'cam_pneu':pneu ,'cam_cons':consommation   })      
            flash('Ce camion a été bien ajouté', 'success')
        return render_template('pages/ajouter_camion.html')

    return render_template('pages/ajouter_camion.html')
    #***********************************************************************************************Editer un Camion********************************************************************
@app.route('/modification_camion', methods=['GET','post'])
def edit_camion():
    rech_cam=''
    cam_select=''
    cam_info=[ '' for i in range(9)]
    liste_camion= con.execute(text("select camion_id, camion_mat, camion_cap, camion_etat, camion_type, camion_tonnage, camion_fonction, camion_assurance, camion_loyer, camion_entretien, camion_pneus, camion_conso   from camion  where camion_actif=1")).fetchall()
    data={ 'liste_camion': liste_camion,
            'rech_cam':rech_cam, 
            'cam_info':cam_info
         }
       
    if request.method=='POST':
        # Si l utilisateur a tapé un nom dans la bare de recherche:
        if request.form['rech_cam']:
            rech_cam=request.form['rech_cam']
            liste_cam_rech=con.execute(text("select camion_id, camion_mat, camion_cap, camion_etat, camion_type, camion_tonnage, camion_fonction, camion_assurance, camion_loyer, camion_entretien, camion_pneus, camion_conso from camion  where  (camion_mat LIKE :cam or camion_type LIKE :cam)  and camion_actif=1 "), {'cam': rech_cam +'%'}).fetchall()
            if liste_cam_rech:
                data['liste_camion']=liste_cam_rech
            else:
                flash(' aucun camion avec cette Immatriculation','danger')
            return render_template('pages/edit_camion.html', **data)   
        # si l utilisateur a coché un nom:
            
            
        if request.form['cam_select']!='':
            cam_select=request.form['cam_select']
            cam_info=con.execute(text("select camion_id, camion_mat, camion_cap, camion_etat, camion_type, camion_tonnage, camion_fonction, camion_assurance, camion_loyer, camion_entretien, camion_pneus, camion_conso from camion  where camion_id=:cam and  camion_actif=1"), {'cam':cam_select}).fetchone()
            data['cam_info']=cam_info
            #return render_template('pages/modifier_chauf.html', **data)
        
    return render_template('pages/edit_camion.html', **data) 
    #**********************************************************************************VALIDER MODIFICATION CHAUFFEUR*****************************************************************

@app.route('/camion_supprimé', methods=['GET','post'])
def camion_supprime():
    #cam_id=request.form['cam_select']
    #cam_id=request.form.get('cam_select')
    camion_id=request.form['camion_id']
    con.execute(text("update camion set camion_actif=0 where camion_id=:camion_id"),{'camion_id':camion_id})
    flash('Le camion coché a été bien supprimé', 'success')   
     
    return redirect(url_for('edit_camion'))  

#**********************************************************************************VALIDER MODIFICATION CHAUFFEUR*****************************************************************

@app.route('/camion_modifié', methods=['GET','post'])
def camion_modifie():
    #cam_id=request.form['cam_select']
    #cam_id=request.form.get('cam_select')
    mat_anc=request.form['mat_anc']
    #cam_id=con.execute(text("select camion_id from camion where camion_mat=:mat_anc"),{'mat_anc': mat_anc}).fetchone()
    cam_id=request.form['cam_id']
    mat=request.form['mat']
    cap=request.form['cap']
    etat=request.form.getlist('etat')
    typeC=request.form.getlist('liste_type')
    tonnage=request.form['tonnage']
    fonction=request.form.getlist('fonction')
    assurance=request.form['assurance'] 
    loyer=request.form['loyer']
    entretien=request.form['entretien'] 
    pneus=request.form['pneus']
    consomation=request.form['consomation']
    print("affichageeeeeeeee",cam_id,mat_anc,  mat,cap,etat[0], typeC[0],tonnage, fonction[0], assurance, loyer, entretien, pneus, consomation,cam_id[0] )
    test_nv_mat=con.execute(text("select camion_mat from camion where camion_mat=:mat and camion_mat<>:mat_anc"),{"mat":mat,'mat_anc':mat_anc}).fetchone()
    print("testtttttttttttttttt nouvaeu mat",test_nv_mat)
    if test_nv_mat:
        flash('La nouvelle immatriculation que vous venez de taper existe déjà, veuillez la modifier!', 'danger')
    else: 
        con.execute(text("update camion set camion_mat=:mat, camion_cap=:cap,camion_etat=:etat,camion_type=:typeC,camion_tonnage=:tonnage,camion_fonction=:fonction,camion_assurance=:assurance,camion_loyer=:loyer, camion_entretien=:entretien, camion_pneus=:pneus,camion_conso=:conso where camion_id=:cam_id"),{'mat':mat,"cap":cap, 'etat':int(etat[0]), 'typeC':typeC[0],'tonnage':tonnage, 'fonction':fonction[0], 'assurance':assurance, 'loyer':loyer, 'entretien': entretien,'pneus':pneus, 'conso':consomation, 'cam_id':cam_id[0]})
        flash('les  modifications ont été bien prises en compte', 'success')   
     
    return redirect(url_for('edit_camion'))  
    
#****************************************************************************************************************ESPACE CHAUFFEUR*********************************************************************************

@app.route('/chauffeur', methods=['GET','post'])
def espace_chauf():
     
    return render_template('pages/espace_chauf.html')
#***************************************************************************************************************************CONTACT********************************************************************************
@app.route('/contact', methods=['GET','post'])
def contact():
    requeteLivraison = pd.read_sql_query('SELECT e.enseigne_intitulé AS enseigne, m.magasin_id, magasin_tarif_rolls, magasin_tarif_palette, magasin_tarif_boxe FROM camion_magasin cm join magasin as m on m.magasin_id = cm.magasin_id join enseigne as e on e.enseigne_id = m.enseigne_id where date between "2020-01-10" and "2021-01-01"', engine)

    dataLivraison = pd.DataFrame(requeteLivraison)
    ens=dataLivraison["enseigne"].value_counts()
    ens=ens.reset_index()
    ens=ens.rename(columns={'enseigne':'Nbre_mag_livrés', 'index':'enseigne'})
       
    data = [go.Pie(labels=ens.enseigne, values=ens.Nbre_mag_livrés, title='Répartition des magasins livrés par enseigne')] 
    #fig = px.pie(df, values='tip', names='day')
    #data = [px.pie(ens, values='Nbre_mag_livrés', names='enseigne', title='Répartition des magasins livrés par enseigne pour la période du 2020-10-10 au 2020-11-24')]
    #data = [go.Bar(x=dataLivraison.enseigne,y=dataLivraison.magasin_tarif_rolls)]
    #fig.update_traces(textposition='inside', textinfo='percent+label')
    
    graphJSON1 = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)

    requeteCasino = pd.read_sql_query('SELECT e.enseigne_intitulé AS enseigne, m.magasin_id, magasin_tarif_rolls, magasin_tarif_palette, magasin_tarif_boxe FROM camion_magasin cm join magasin as m on m.magasin_id = cm.magasin_id join enseigne as e on e.enseigne_id = m.enseigne_id where date between "2020-10-10" and "2021-01-01" and magasin_tarif_rolls <>-1 and e.enseigne_intitulé="CASINO"', engine)
    rolls = pd.DataFrame(requeteCasino)
    rolls= requeteCasino['magasin_tarif_rolls'].value_counts()
    rolls=rolls.reset_index()
    rolls=rolls.rename(columns={'index':'Tarif_Rolls', 'magasin_tarif_rolls':'Nbre_mag'})
    data1 = [go.Pie(labels=rolls.Tarif_Rolls, values=rolls.Nbre_mag, title='Répartition Tarif Rolls pour Casino')] 
    graphJSON2 = json.dumps(data1, cls=plotly.utils.PlotlyJSONEncoder)
    """fig.show()
    #data = [go.Bar(x=dataLivraison.enseigne,y=dataLivraison.magasin_tarif_rolls)]
    graphJSON1 = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)
    trace_acteur = go.Bar(x=dataLivraison.enseigne, y=dataLivraison.magasin_tarif_rolls, name='Enseigne', marker=dict(color='#A2D5F2'))

    trace_directeur = go.Bar(x=dataLivraison.enseigne, y=dataLivraison.magasin_tarif_palette, name='Palletes', marker=dict(color='#59606D'))

    data = [trace_acteur, trace_directeur]

    graphJSON2 = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)"""
        
    return render_template('pages/diagram_apres_tournees.html',plot1=graphJSON1, plot2=graphJSON2)
#**************************************************************************************************************************AJOUTER CHAUFFEUR**********************************************************************
#
@app.route('/ajouter_chauf', methods=['GET','post'])
def ajouter_chauf():
    liste_contrat=con.execute(text("select contrat_id, contrat_intitule from contrat")).fetchall()
    data={ 'liste_contrat':liste_contrat}
    if request.method=='POST':
        nom=request.form['nom']
        prenom=request.form['prenom']
        cout=request.form['horaire']
        panier1=request.form['panier1']
        panier2=request.form['panier2']
        panier3=request.form['panier3']
        #con.execute(text(insert into chauffeur ))
    return render_template('pages/ajouter_chauf.html',**data)

    #**************************************************************************************Ajouter Contrat à un chauffeur**********************************************************
@app.route('/ajout_contrat', methods=['GET','post'])
def ajouter_contrat_chauf():
    
    #liste chauffeurs
    requete_chauf="select chauf_id, chauf_nom, chauf_prenom, concat(chauf_nom,'---' ,chauf_prenom) as NP from chauffeur where chauf_actif=1"
    liste_chauf=con.execute(text(requete_chauf)).fetchall()
    
     #liste statuts
    requete_contrat=" select contrat_id, contrat_intitule from contrat"
    liste_contrat=con.execute(text(requete_contrat)).fetchall()

    
    data={
                'liste_chauf':liste_chauf,
                'liste_contrat':liste_contrat,
                
         }
    if request.method== 'POST':
        chauf_id=request.form['liste_chauf']  
        contrat_id=request.form['liste_contrat']
        date_debut=request.form['date_D']
        date_fin=request.form['date_F']
        requete_date_fin=' select chauf_id, date_fin from chauffeur_contrat where chauf_id=:chauf_id and (date_fin > :date_debut) '  
        ver_date_fin=con.execute(text(requete_date_fin), {'chauf_id':chauf_id , 'date_debut':date_debut}).fetchall()
        
        if date_debut>date_fin:
            flash('la date fin doit être supperieure à la date début', 'danger')
        elif ver_date_fin :
            flash('ce chauffeur a déjà un contrat en cours de cette période, si vous voulez lui attribuer un autre, veuillez liu arrêter son contrat à cette période en allant sur editer contrat chauffeur', 'danger') 
        else:
            con.execute(text('insert into chauffeur_contrat (chauf_id, contrat_id, date_debut, date_fin) values (:chauf_id, :contrat_id, :date_debut, :date_fin)'), {'chauf_id':chauf_id, 'contrat_id':contrat_id, 'date_debut': date_debut, 'date_fin': date_fin})    
            flash('ce contrat a été ajouté avec succès à ce chauffeur', 'success') 
        
            
    
    return render_template('pages/ajouter_contrat_chauf.html', **data)    


  #resultat_pseudo=request.args.get('resultat_pseudo')
  #*************************************************************************************************************VALIDER MODIFICATION CONTRAT CHAUFFEUR**************************************************************
@app.route('/chaufeur_contrat_modifié', methods=['GET','post']) # post de edit_contrat_chauf
def chauffeur_contrat_modifie():
    chauf_id=request.form['modal_chauf_id'] 
    anc_contrat_id=request.form['modal_anc_contrat_id']
    nv_contrat_id=request.form['modal_liste_contrat']
    anc_date_fin=request.form['modal_anc_date_fin']
    anc_date_deb=request.form['modal_anc_date_deb']
    nv_date_deb=request.form['modal_date_debut']
    nv_date_fin=request.form['modal_date_fin']
    test_contrat=con.execute(text("select chauf_id from chauffeur_contrat where chauf_id=:chauf_id and date_fin> :nv_date_deb and (contrat_id<>:anc_contrat_id and date_debut<>:anc_date_deb and date_fin<>:anc_date_fin)"),{'chauf_id':chauf_id, 'nv_date_deb':nv_date_deb, 'anc_contrat_id':anc_contrat_id, 'anc_date_deb':anc_date_deb,'anc_date_fin':anc_date_fin}).fetchone()
    if nv_date_deb>nv_date_fin:
            flash('la date fin doit être supperieure à la date début', 'danger')
    elif test_contrat:  
         flash('Veuillez vérifier la date début, elle est comprise dans un autre contrat de ce chauffeur', 'danger')   
    else :
        con.execute(text("update chauffeur_contrat set chauf_id=:chauf_id, contrat_id=:nv_contrat_id, date_debut=:nv_date_deb, date_fin=:nv_date_fin where chauf_id=:chauf_id and contrat_id=:anc_contrat_id and date_debut=:anc_date_deb and date_fin= :anc_date_fin"),{'chauf_id':chauf_id, 'nv_contrat_id':nv_contrat_id,'nv_date_deb':nv_date_deb,'nv_date_fin':nv_date_fin, 'anc_contrat_id':anc_contrat_id , 'anc_date_deb':anc_date_deb ,'anc_date_fin': anc_date_fin})
        flash('les modifications ont été bien prises en compte', 'success')
    return redirect(url_for('edit_contrat_chauf'))
    #**************************************************************************************************************VALIDER SUPPRESSION CONTRAT CHAUFFEUR**********************************************************************
@app.route('/chaufeur_contrat_supprime', methods=['GET','post'])
def chauffeur_contrat_supprime():#++++++++++++++++++++++++++++++++++++UPDATE ne marche pas 
    chauf_id=request.form['chauf_id']
    contrat_id=request.form['contrat_id']
    date_debut=request.form['date_deb']
    date_fin=request.form['date_fin']
    con.execute(text("delete from chauffeur_contrat where chauf_id=:chauf_id and contrat_id=:contrat_id and date_debut=:date_debut and date_fin=:date_fin"),{'chauf_id':chauf_id, 'contrat_id':contrat_id, 'date_debut':date_debut,'date_fin':date_fin})
    flash('Ce Contrat a été bien suppirmé pour ce Chauffeur', 'success')
    return redirect(url_for('edit_contrat_chauf'))
    
#************************************************************************************************EDITER CONTRAT CHAUFFEUR********************************************************************************************************************************************
@app.route('/modification_contrat_chauffeur', methods=['GET','post'])
def edit_contrat_chauf():
    rech_chauf=''
    chauf_select=''
    chauf_info=[ '' for i in range(9)]
    liste_chauf= con.execute(text("select chauf_nom, chauf_prenom, contrat_intitule, date_debut, date_fin, chauffeur.chauf_id , contrat.contrat_id  from chauffeur left join  chauffeur_contrat on chauffeur_contrat.chauf_id= chauffeur.chauf_id left join contrat on contrat.contrat_id = chauffeur_contrat.contrat_id where date_fin>date(now()) and chauf_actif=1")).fetchall()
    liste_contrat=con.execute(text("select contrat_id, contrat_intitule from contrat")).fetchall()
    
    data={ 'liste_chauf': liste_chauf,
            'rech_chauf':rech_chauf, 
            'chauf_info':chauf_info,
            'liste_contrat': liste_contrat,
            
    }
       
    if request.method=='POST':
        # Si l utilisateur a tapé un nom dans la bare de recherche:
        chauf_select=request.form.getlist('chauf_select')
        print("chaufeeuuuuuuuuuuur radio", int(chauf_select[0])+2)
        if request.form['rech_chauf']:
            rech_chauf=request.form['rech_chauf']
            liste_chauf_rech=con.execute(text("select chauf_nom, chauf_prenom, contrat_intitule, date_debut, date_fin,chauffeur.chauf_id , contrat.contrat_id    from chauffeur left join  chauffeur_contrat on chauffeur_contrat.chauf_id= chauffeur.chauf_id left join contrat on contrat.contrat_id = chauffeur_contrat.contrat_id where (date_fin>date(now()) or date_fin is null) and chauf_actif=1 and (chauf_nom LIKE :chauf or chauf_prenom LIKE :chauf_pr )"), {'chauf':rech_chauf +'%', 'chauf_pr':rech_chauf +'%'}).fetchall()
            if liste_chauf_rech:
                data['liste_chauf']=liste_chauf_rech
            else:
                flash(' aucun chauffeur avec ce nom','danger')
            return render_template('pages/edit_contrat_chauf.html', **data)   
        # si l utilisateur a coché un nom:
                   
        if request.form['chauf_select']!='':
            chauf_select=request.form['chauf_select']
            chauf_info=con.execute(text("select chauf_nom, chauf_prenom, contrat_intitule, date_debut, date_fin, chauffeur.chauf_id , contrat.contrat_id    from chauffeur left join  chauffeur_contrat on chauffeur_contrat.chauf_id= chauffeur.chauf_id left join contrat on contrat.contrat_id = chauffeur_contrat.contrat_id where chauffeur.chauf_id=:chauf_select and chauf_actif=1 and (date_fin>date(now()) or date_fin is null) "), {'chauf_select':chauf_select}).fetchone()
            data['chauf_info']=chauf_info
            #return render_template('pages/edit_statut_chauf.html', **data)
       
    return render_template('pages/edit_contrat_chauf.html', **data)   
  

#**************************************************************************************************************VALIDER SUPPRESSION CHAUFFEUR**********************************************************************
@app.route('/chaufeur_supprime', methods=['GET','post'])
def chauffeur_supprime():#++++++++++++++++++++++++++++++++++++UPDATE ne marche pas 
    chauf_id=request.form['chauf_id']
    contra_date_fin=request.form['contra_date_fin']
    contrat_encours=con.execute(text("select date_debut from chauffeur_contrat where chauf_id=:chauf_id and date_fin>:contra_date_fin "),{'chauf_id':chauf_id,'contra_date_fin':contra_date_fin}).fetchall()
    if contrat_encours:
        if len(contrat_encours)>1:
            flash("il existe plus d'un contrat à cette date veuillez les supprimer sur edit contrat chauffeur ou vérifier bien la saisie de la date fin du contrat en cours", 'danger')    
            return redirect(url_for('modifier_chauffeur'))
        elif contrat_encours[0][0]> datetime.strptime(contra_date_fin, '%Y-%m-%d').date():
            flash(" Veuillez vérifier la date fin du contrat, elle est inférieure à la date début du contrat en cours", 'danger')    
            return redirect(url_for('modifier_chauffeur'))
                
    statut_encours=con.execute(text("select date_debut from chauffeur_statut where chauff_id=:chauf_id and date_fin> :contra_date_fin"),{'chauf_id':chauf_id,'contra_date_fin':contra_date_fin}).fetchall()    
    if statut_encours:
        if len(statut_encours)>1:
            flash("il existe plus d'un statut indisponible à cette date veuillez les supprimer sur edit statut chauffeur ou vérifier bien la saisie de la date fin du contrat en cours", 'danger')    
            return redirect(url_for('modifier_chauffeur'))
        elif statut_encours[0][0]> datetime.strptime(contra_date_fin, '%Y-%m-%d').date():
            flash(" Veuillez vérifier la date fin du contrat, elle est inférieure à la date début d'un statut en cours", 'danger')    
            return redirect(url_for('modifier_chauffeur'))
       
    #con.execute=(text("update chauffeur_statut set date_fin=:contra_date_fin where chauf_id=:chauf_id and date_fin> :contra_date_fin"),{'chauf_id':chauf_id, 'contra_date_fin':contra_date_fin})    
    #con.execute=(text("update chauffeur_contrat set date_fin=:contra_date_fin where chauf_id=:chauf_id and date_fin> :contra_date_fin"),{'chauf_id':chauf_id, 'contra_date_fin':contra_date_fin})
    #con.execute(text("update chauffeur set chauf_actif=0 where chauf_id=:chauf_id"),{'chauf_id':chauf_id})    
    flash('Ce chauffeur a été bien supprimé', 'success')
    return redirect(url_for('modifier_chauffeur'))

 #*************************************************************************************************************VALIDER MODIFICATION STATUT CHAUFFEUR**************************************************************
@app.route('/chaufeur_statut_modifié', methods=['GET','post']) # post de edit_statut_chauf
def chauffeur_statut_modifie():
    chauf_id=request.form['modal_chauf_id'] 
    anc_statut_id=request.form['modal_anc_stat_id']
    nv_statut_id=request.form['modal_liste_statut']
    anc_date_fin=request.form['modal_anc_date_fin']
    anc_date_deb=request.form['modal_anc_date_deb']
    nv_date_deb=request.form['modal_date_debut']
    nv_date_fin=request.form['modal_date_fin']
    if nv_date_deb>nv_date_fin:
            flash('la date fin doit être supperieure à la date début', 'danger')
    elif anc_statut_id =="None":
        test_statut_vide=con.execute(text("select chauff_id from chauffeur_statut where chauff_id=:chauf_id and date_fin> :nv_date_deb"),{'chauf_id':chauf_id, 'nv_date_deb':nv_date_deb}).fetchone()
        if test_statut_vide:
            flash('Veuillez vérifier la date début, elle est comprise dans un autre statut pour ce chauffeur', 'danger')   
        else:
            con.execute(text("insert into chauffeur_statut (chauff_id,statut_id,date_debut,date_fin) values (:chauf_id, :nv_statut_id, :date_deb, :date_fin)"),{'chauf_id':chauf_id, 'nv_statut_id':nv_statut_id,'date_deb':nv_date_deb,'date_fin':nv_date_fin} )    
            flash('les modifications ont été bien prises en compte', 'success')
    else:       
        test_statut=con.execute(text("select chauff_id from chauffeur_statut where chauff_id=:chauf_id and date_fin> :nv_date_deb and (statut_id<>:anc_statut_id and date_debut<>:anc_date_deb and date_fin<>:anc_date_fin)"),{'chauf_id':chauf_id, 'nv_date_deb':nv_date_deb, 'anc_statut_id':anc_statut_id, 'anc_date_deb':anc_date_deb,'anc_date_fin':anc_date_fin}).fetchone()
        if test_statut:
            flash('Veuillez vérifier la date début, elle est comprise dans un autre statut pour ce chauffeur', 'danger') 
        else:   
            con.execute(text("update chauffeur_statut set chauff_id=:chauf_id, statut_id=:nv_statut_id, date_debut=:nv_date_deb, date_fin=:nv_date_fin where chauff_id=:chauf_id and statut_id=:anc_statut_id and date_debut=:anc_date_deb and date_fin= :anc_date_fin"),{'chauf_id':chauf_id, 'nv_statut_id':nv_statut_id,'nv_date_deb':nv_date_deb,'nv_date_fin':nv_date_fin, 'anc_statut_id':anc_statut_id , 'anc_date_deb':anc_date_deb ,'anc_date_fin': anc_date_fin})
            flash('les modifications ont été bien prises en compte', 'success')
    return redirect(url_for('edit_staut_chauf'))
     


#***********************************************************************************EDITER STATUT CHAUFFEUR********************************************************************************************************************************************
@app.route('/modification_statut_chauffeur', methods=['GET','post'])
def edit_staut_chauf():
    rech_chauf=''
    chauf_select=''
    chauf_info=[ '' for i in range(9)]
    liste_chauf= con.execute(text("select chauf_nom, chauf_prenom, statut_intitule, date_debut, date_fin, chauf_id , statut.statut_id  from chauffeur left join  chauffeur_statut on chauffeur_statut.chauff_id= chauffeur.chauf_id left join statut on statut.statut_id = chauffeur_statut.statut_id where (date_fin>date(now()) or date_fin is null) and chauf_actif=1")).fetchall()
    liste_statut=con.execute(text("select statut_id, statut_intitule from statut")).fetchall()
    data={ 'liste_chauf': liste_chauf,
            'rech_chauf':rech_chauf, 
            'chauf_info':chauf_info,
            'liste_statut': liste_statut,
            'test':'bonjour'
    }
       
    if request.method=='POST':
        # Si l utilisateur a tapé un nom dans la bare de recherche:
        
        if request.form['rech_chauf']:
            rech_chauf=request.form['rech_chauf']
            liste_chauf_rech=con.execute(text("select chauf_nom, chauf_prenom, statut_intitule, date_debut, date_fin, chauf_id , statut.statut_id   from chauffeur left join  chauffeur_statut on chauffeur_statut.chauff_id= chauffeur.chauf_id left join statut on statut.statut_id = chauffeur_statut.statut_id where (date_fin>date(now()) or date_fin is null) and chauf_actif=1 and (chauf_nom LIKE :chauf or chauf_prenom LIKE :chauf_pr )"), {'chauf':rech_chauf +'%', 'chauf_pr':rech_chauf +'%'}).fetchall()
            if liste_chauf_rech:
                data['liste_chauf']=liste_chauf_rech
            else:
                flash(' aucun chauffeur avec ce nom','danger')
            return render_template('pages/edit_statut_chauf.html', **data)   
        # si l utilisateur a coché un nom:
                   
        if request.form['chauf_select']!='':
            chauf_select=request.form['chauf_select']
            chauf_info=con.execute(text("select chauf_nom, chauf_prenom, statut_intitule, date_debut, date_fin, chauf_id, statut.statut_id   from chauffeur left join  chauffeur_statut on chauffeur_statut.chauff_id= chauffeur.chauf_id left join statut on statut.statut_id = chauffeur_statut.statut_id where chauf_id=:chauf_select and chauf_actif=1 and (date_fin>date(now()) or date_fin is null) "), {'chauf_select':chauf_select}).fetchone()
            data['chauf_info']=chauf_info
            #return render_template('pages/edit_statut_chauf.html', **data)
       
    return render_template('pages/edit_statut_chauf.html', **data)   
#**************************************************************************************Ajouter statut à un chauffeur**********************************************************
@app.route('/ajout_statut', methods=['GET','post'])
def ajouter_statut_chauf():
    
    #liste chauffeurs
    requete_chauf="select chauf_id, chauf_nom, chauf_prenom, concat(chauf_nom,'---' ,chauf_prenom) as NP from chauffeur where chauf_actif=1"
    liste_chauf=con.execute(text(requete_chauf)).fetchall()
    
     #liste statuts
    requete_statu=" select STATUT_ID, STATUT_INTITULE from statut"
    liste_statut=con.execute(text(requete_statu)).fetchall()

    
    data={
                'liste_chauf':liste_chauf,
                'liste_statut':liste_statut,
                
         }
    if request.method== 'POST':
        chauf_id=request.form['liste_chauf']  
        statut_id=request.form['liste_statut']
        date_debut=request.form['date_D']
        date_fin=request.form['date_F']
        requete_date_fin=' select chauff_id, date_fin from chauffeur_statut where chauff_id=:chauf_id and (date_fin > :date_debut) '  
        ver_date_fin=con.execute(text(requete_date_fin), {'chauf_id':chauf_id , 'date_debut':date_debut}).fetchall()
        
        if date_debut>date_fin:
            flash('la date fin doit être supperieure à la date début', 'danger')
        elif ver_date_fin :
            flash('ce chauffeur a déjà un statut pour cette date', 'danger') 
        else:
            con.execute(text('insert into chauffeur_statut (chauff_id, statut_id, date_debut, date_fin) values (:chauf_id, :statut_id, :date_debut, :date_fin)'), {'chauf_id':chauf_id, 'statut_id':statut_id, 'date_debut': date_debut, 'date_fin': date_fin})    
            flash('ce statut a été ajouté avec succès à ce chauffeur', 'success') 
        
            
    
    return render_template('pages/ajouter_statut_chauf.jinja', **data)    




#***********************************************************************************************Editer un Chauffeur********************************************************************
@app.route('/modification_chauffeur', methods=['GET','post'])
def modifier_chauffeur():
    rech_chauf=''
    chauf_select=''
    chauf_info=[ '' for i in range(9)]
    liste_chauf= con.execute(text("select chauf_nom, chauf_prenom, chauf_cout_horaire, chauff_panier1, chauff_panier2, chauff_panier3, chauf_id  from chauffeur  where chauf_actif=1")).fetchall()
    data={ 'liste_chauf': liste_chauf,
            'rech_chauf':rech_chauf, 
            'chauf_info':chauf_info,
            'test':'bonjour'
         }
       
    if request.method=='POST':
        # Si l utilisateur a tapé un nom dans la bare de recherche:
        if request.form['rech_chauf']:
            rech_chauf=request.form['rech_chauf']
            liste_chauf_rech=con.execute(text("select chauf_nom, chauf_prenom, chauf_cout_horaire, chauff_panier1, chauff_panier2, chauff_panier3, chauf_id   from chauffeur  where  (chauf_nom LIKE :chauf or chauf_prenom LIKE :chauf)  and chauf_actif=1 "), {'chauf': rech_chauf +'%'}).fetchall()
            if liste_chauf_rech:
                data['liste_chauf']=liste_chauf_rech
            else:
                flash(' aucun chauffeur avec ce nom','danger')
            return render_template('pages/modifier_chauf.html', **data)   
        # si l utilisateur a coché un nom:
            
            
        if request.form['chauf_select']!='':
            chauf_select=request.form['chauf_select']
            chauf_info=con.execute(text("select chauf_nom, chauf_prenom, chauf_cout_horaire, chauff_panier1, chauff_panier2, chauff_panier3, chauf_id from chauffeur  where chauf_id=:chauf_select and  chauf_actif=1"), {'chauf_select':chauf_select}).fetchone()
            data['chauf_info']=chauf_info
            #return render_template('pages/modifier_chauf.html', **data)
        
    return render_template('pages/modifier_chauf.html', **data)   
#**********************************************************************************VALIDER MODIFICATION CHAUFFEUR*****************************************************************

@app.route('/chaufeur_modifié', methods=['GET','post'])
def chauffeur_modifie():
    chauf_id=request.form['chauf_id']
    nom=request.form['nom'] 
    prenom=request.form['prenom']
    print('formulailre de la fenetre modale envoyée avec succes', nom, prenom)
    return render_template('pages/modifier_chauf.html')   
    
#***********************************************************************************************************************Ajouter un utilisateur*********************************************************************

@app.route('/ajout_utilisateur', methods=['GET','post'])
def ajouter_user():
    Fpseudo=''
    Frole,Fmdp,FCmdp,Fnom,Fprenom='','','','',''
    requete_role="select role_id, role_intitule from role"
    role=con.execute(text(requete_role)).fetchall()
    role_n=[row[0] for row in role]
    nbre_role=len(role_n)
    data={
                'role_selec':Frole,
                'role':role,
                'nbre_role' : nbre_role,
                'pseudo':Fpseudo,
                'mdp':Fmdp,
                'Cmpd':FCmdp,
                'nom':Fnom,
                'prenom':Fprenom
         }
    if request.method =='POST':
        Frole=request.form['liste_roles']
        Fpseudo=request.form['pseudo']
        Fnom=request.form['nom']
        Fprenom=request.form['prenom']
        Fmdp=request.form['mdp']
        FCmdp=request.form['Cmdp']
        requet_pseudo=text('select utilisateur_id from utilisateur where utilisateur_pseudo=:pseudo')
        pseudo=con.execute(requet_pseudo,{'pseudo':Fpseudo}).fetchone()
        
        if pseudo:
            flash('ce pseudo existe déjà, veuillez le changer', 'danger')
        elif request.form['mdp'] != request.form['Cmdp']:
            flash('les deux mots de passe ne correspondent pas','danger')
        else:
            Fmdp=hashlib.sha1(str.encode(Fmdp)).hexdigest()
            #requete_ajout="call create_utilisateur(:nom,:prenom,:mdp,:pseudo, :role)"
           
            """conect = pymysql.connect(host='localhost', user='simplon', password='Simplon2020', db='perrenot', cursorclass= pymysql.cursors.DictCursor)

            try:
                curseur = conect.cursor()
                curseur.execute("call create_utilisateur(?, ?, ?, ?, ?)", ('Janvier','fevier','mars','pseudo', 2))

            except Exception as e:
                print("exception occured: {}".format (e))

            finally:
                conect.close()
            curseur = conect.cursor()"""
            #curseur.execute("call create_utilisateur(?, ?, ?, ?, ?)", ['Janvier','fevier','mars','pseudo', 2])
            requete_ajout="INSERT INTO utilisateur (utilisateur_nom, utilisateur_prenom, utilisateur_MDP, utilisateur_pseudo, role_id) VALUES (:nom, :prenom, :mdp, :pseudo,:role)"

            con.execute(text(requete_ajout),{'nom': Fnom, 'prenom':Fprenom, 'mdp':Fmdp, 'pseudo':Fpseudo,'role':Frole})
            #con.execute(text("call create_utilisateur('Janvier','fevier','mars','pseudo', 2)"))
            flash("l'utilisateur a été bien enregistré", 'success')
            Fpseudo=''
            Fnom=''
            Fprenom=''
            Fmdp=''
            FCmdp=''
            Frole=''
        data['pseudo']=Fpseudo 
        data['nom']  =Fnom 
        data['prenom']=Fprenom
        data['mdp']=Fmdp
        data['role_selec']=Frole
        return render_template('pages/ajouter_utilisateur.jinja', **data)   
        
    else:
        
        return render_template('pages/ajouter_utilisateur.jinja', **data)    

#*******************************************************************************************Ajouter un MAGASN**************************************************************************
@app.route('/ajout_magasin', methods=['GET','post'])
def ajouter_magasin():
    Fcode=''
    Fadresse=''
    Fheure=''
    Frolls=0
    Fpal=0
    Fbox=0
    Fenseigne=''
    requete_ens="select enseigne_id, enseigne_intitulé from enseigne"
    enseigne=con.execute(text(requete_ens)).fetchall()
    ens_n=[row[0] for row in enseigne]
    nbre_ens=len(ens_n)
    data={
                'code':Fcode,
                'adresse':Fadresse,
                'heure' : Fheure,
                'rolls':Frolls,
                'palette':Fpal,
                'boxe':Fbox,
                'nbre_ens':nbre_ens,
                'enseigneS':Fenseigne,
                'enseigne':enseigne
         }
    if request.method =='POST':
        Fcode=request.form['code']
        Fadresse=request.form['adresse']
        Fheure=request.form['heure']
        Frolls=request.form['rolls']
        Fpal=request.form['palette']
        Fbox=request.form['boxe']
        Fenseigne=request.form['liste_ens']
        requet_magasin=text('select magasin_id from magasin where magasin_code=:code and enseigne_id=:enseigne and magasin_actif=1')
        magasin=con.execute(requet_magasin,{'code':Fcode, 'enseigne':Fenseigne}).fetchone()
        magasin_sup=con.execute(text("select magasin_id from magasin where magasin_code=:code and enseigne_id=:enseigne and magasin_actif=0"),{'code':Fcode, 'enseigne':Fenseigne}).fetchone()
        if magasin:
            flash('ce code magasin existe déjà pour cette enseigne, veuillez le changer!', 'danger')
        elif magasin_sup:
            con.execute(text("update magasin set magasin_actif=1, magasin_adresse=:mag_adr, magasin_heure_livr=:heure_livr, magasin_tarif_rolls=:tarif_rolls, magasin_tarif_palette=:tarif_pal where magasin_id= :mag_id "),{'mag_id':magasin_sup[0], 'mag_adr': Fadresse ,'heure_livr': Fheure,'tarif_rolls': Frolls,'tarif_pal': Fpal })
            flash('ce code magasin supprimé existait déjà pour cette enseigne, il a été récupéré', 'success')   
        else:
            requete_ajout="INSERT INTO magasin (magasin_code, magasin_adresse, magasin_heure_livr, magasin_tarif_rolls, enseigne_id, magasin_tarif_palette, magasin_tarif_boxe) VALUES (:code, :adresse, :heure, :rolls,:enseigne, :pal, :boxe)"
            con.execute(text(requete_ajout),{'code': Fcode, 'adresse':Fadresse, 'heure':Fheure, 'rolls':Frolls,'enseigne':Fenseigne,'pal':Fpal, 'boxe':Fbox})
            flash("le magasin a été bien enregistré", 'success')
            Fcode=''
            Fadresse=''
            Fheure=''
            Frolls=''
            Fpal=''
            Fbox=''
            Fenseigne=''
            return redirect(url_for('ajouter_magasin'))
        data['code']=Fcode
        data['adresse']  =Fadresse 
        data['heure']=Fheure
        data['rolls']=Frolls
        data['palette']=Fpal
        data['boxe']=Fbox
        data['enseigneS']=Fenseigne
        return render_template('pages/ajouter_magasin.html', **data)   
        
    else:
        
        return render_template('pages/ajouter_magasin.html', **data)  
#*************************************************************************************************MAGASIN_SUPPRIME*********************************************************
@app.route('/suppression_enregistrée', methods=['GET','post']) # post de edit_statut_chauf
def magasin_supprime():
    mag_id=request.form['mag_id'] 
    con.execute(text("update magasin set magasin_actif=0 where magasin_id=:mag_id"),{'mag_id':mag_id})
    flash('Le magasin coché a été bien supprimé', 'success')
          
    return redirect(url_for('editer_magasin'))
#*************************************************************************************************MAGASIN_MODIFE*************************************************************
@app.route('/modification_enregistrée', methods=['GET','post']) # post de edit_statut_chauf
def magasin_modifie():
    anc_ens_id=request.form['enseigne_id'] 
    mag_code=request.form['code']
    adresse=request.form['adresse']
    heure_livraison=request.form['heure_livr']
    tarif_rolls=request.form['tarif_rolls']
    tarif_pal=request.form['tarif_pal']
    anc_code_mag=request.form['anc_code_mag']
    nv_ens_id=request.form.getlist('modal_ensNv')
    test_mag_id=con.execute(text("select magasin_id from magasin where magasin_code=:mag_code and enseigne_id=:ens_id and magasin_code<>:anc_code_mag"),{'mag_code':mag_code, 'ens_id': nv_ens_id, 'anc_code_mag':anc_code_mag }).fetchone()
    if test_mag_id:
        flash('Ce code magsin existe déjà pour cette enesigne, veuillez le modifier', 'danger')
    else :
        con.execute(text("update magasin set magasin_code=:mag_code,magasin_adresse=:adresse,magasin_heure_livr=:heure_livraison,magasin_tarif_rolls=:tarif_rolls,magasin_tarif_palette=:tarif_pal,enseigne_id=:nv_ens_id where enseigne_id=:anc_ens_id and magasin_code=:anc_code_mag"),{'mag_code':mag_code, 'adresse':adresse,'heure_livraison':heure_livraison,'tarif_rolls':tarif_rolls, 'tarif_pal':tarif_pal , 'nv_ens_id':nv_ens_id ,'anc_ens_id': anc_ens_id, 'anc_code_mag':anc_code_mag})
        flash('les modifications ont été bien prises en compte', 'success')
        
    return redirect(url_for('editer_magasin'))
     
#***********************************************************************************************Editer un Magasin********************************************************************
@app.route('/modification_magasin', methods=['GET','post'])
def editer_magasin():
    rech_mag=''
    mag_select=''
    mag_info=[ '' for i in range(9)]
    liste_enseigne=con.execute(text("select enseigne_id, enseigne_intitulé from enseigne ")).fetchall()
    liste_magasin= con.execute(text("select magasin_id, magasin_code, magasin_adresse, magasin_heure_livr, magasin_tarif_rolls, magasin_tarif_palette, enseigne_intitulé, magasin.enseigne_id    from magasin join enseigne on enseigne.enseigne_id=magasin.enseigne_id  where magasin_actif=1")).fetchall()
    data={ 'liste_magasin': liste_magasin,
            'rech_mag':rech_mag, 
            'mag_info':mag_info,
            'liste_enseigne':liste_enseigne
            
         }
       
    if request.method=='POST':
        # Si l utilisateur a tapé un nom dans la bare de recherche:
        if request.form['rech_mag']:
            rech_mag=request.form['rech_mag']
            liste_mag_rech=con.execute(text("select magasin_id, magasin_code, magasin_adresse, magasin_heure_livr, magasin_tarif_rolls, magasin_tarif_palette, enseigne_intitulé, magasin.enseigne_id from magasin join enseigne on enseigne.enseigne_id=magasin.enseigne_id  where magasin_actif=1 and  (magasin_code LIKE :magC )  and magasin_actif=1 "), {'magC': rech_mag +'%'}).fetchall()
            if liste_mag_rech:
                data['liste_magasin']=liste_mag_rech
            else:
                flash(' Ce code magasin n exsiste pas','danger')
            return render_template('pages/edit_magasin.html', **data)   
        # si l utilisateur a coché un nom:
            
            
        if request.form['mag_select']!='':
            mag_select=request.form['mag_select']
            mag_info=con.execute(text("select magasin_id, magasin_code, magasin_adresse, magasin_heure_livr, magasin_tarif_rolls, magasin_tarif_palette, enseigne_intitulé, magasin.enseigne_id  from magasin join enseigne on enseigne.enseigne_id=magasin.enseigne_id where magasin.magasin_id=:mag_select and  magasin_actif=1"), {'mag_select':mag_select}).fetchone()
            #liste_mag_rech=con.execute(text("select magasin_id, magasin_code, magasin_adresse, magasin_heure_livr, magasin_tarif_rolls, magasin_tarif_palette, enseigne_intitulé    from magasin join enseigne on enseigne.enseigne_id=magasin.enseigne_id  where magasin_actif=1 and  (magasin_code LIKE :magC )  and magasin_actif=1 "), {'magC': rech_mag +'%'}).fetchall()
           
            data['mag_info']=mag_info
            #return render_template('pages/modifier_chauf.html', **data)
        
    return render_template('pages/edit_magasin.html', **data)            



  #resultat_pseudo=request.args.get('resultat_pseudo')
    

#********************************************************************************************************ENREGISTRER TOURNEES***********************************************************
@app.route('/enregistrement_tournée', methods=['get','post']) #post de valider_tournée.html
def enregistrer_tournee():
    if request.method=='POST':
        nom_chauf=request.form.getlist('nom_chauf')
        vlm_rolls=request.form.getlist('vlm_rolls')
        vlm_pal=request.form.getlist('vlm_pal')
        #vlm_box=request.form.getlist('vlm_box')
        mag_code=request.form.getlist('code_mag')
        camion=request.form.getlist('camion')
        date_tour=request.form['date_tour']
        mag_id=request.form.getlist('mag_id')
        nbMag_par_camion=request.form.getlist('Tnbre_mag_cam')
        cpt_mag=-1
        #for cam in range(len(camion)):
        for id, val in enumerate(nbMag_par_camion): 
            if int(val)!=0:
                ligne=1
                #mag_non_sauv=[]
                for i in range(int(val)):
                    cpt_mag+=1
                    print('enregistrement camion',camion[id],'magasin',mag_code[cpt_mag], vlm_pal[cpt_mag], vlm_rolls[cpt_mag], nom_chauf[id])
                    ligneT=con.execute(text("select max(ligne) from chauffeur_camion where camion_id=:camion and date=:date"),{'camion':camion[id], 'date':date_tour}).fetchone()
                    #ligneT=con.execute(text("select ligne from chauffeur_camion where chauf_id=1 and camion_id=1 and date='2020-01-01'")).fetchone()
                    
                    if ligneT[0] is not None:
                        print(" la plus grande ligne", ligneT[0])
                        ligne=int(ligneT[0])+1
                                                
                    con.execute(text(" insert into camion_magasin (camion_id, magasin_id, date, ligne, nbre_rolls, nbre_palette) values(:camion, :mag, :date, :ligne, :rolls, :pal)"), {'camion':camion[id],'mag':mag_id[cpt_mag], 'date':date_tour, 'ligne':ligne, 'rolls':vlm_rolls[cpt_mag], 'pal':vlm_pal[cpt_mag] })
                    con.execute(text("DELETE FROM magasin_journalier WHERE (mag_id = :mag) and (`date` = :date)"),{'mag':mag_id[cpt_mag], 'date':date_tour})

                con.execute(text("insert into chauffeur_camion (chauf_id, camion_id, date,ligne) values (:chauf, :camion, :date, :ligne)"), {'chauf': nom_chauf[id], 'camion':camion[id], 'date':date_tour, 'ligne':ligne})
        con.execute(text("update magasin_journalier set statut_tournée=0 where  date = :date"),{'date':date_tour})
    flash('les tournées ont bien été enregistrées', 'success') 
    
    return render_template('pages/diagram_apres_tournees.html')                   
               
    """for i in range(len(mag_code)):
    print("volumes racuperes avec magasins",vlm_box[i], vlm_pal[i], vlm_rolls[i], mag_code[i])
    for id, val in enumerate(nbMag_par_camion):
    
        print('camion',id, camion[id])
        print(id+1, val)"""
    
#**************************************************************************************************************************************************SELECTION MAGASINS***********************************************************
@app.route('/selection_magasin', methods=['get','post'])
def selection_magasins():

    requete_nbre_ens='select count(*) from enseigne where enseigne_actif=1'
    nbre_ens=con.execute(text(requete_nbre_ens)).fetchone()[0]
    requete_ens='select enseigne_id,enseigne_intitulé from enseigne where enseigne_actif=1'
    liste_enseigne=con.execute(text(requete_ens)).fetchall()
    
    requete_camion="call liste_camion()"
    camion=con.execute(text(requete_camion)).fetchall()
    
   
    liste_mag=[con.execute(text("select magasin_code,magasin_id from magasin where enseigne_id=:enseigne and magasin_actif=1"),{'enseigne':liste_enseigne[j][0]}).fetchall() for j in range(len(liste_enseigne))]
       
    # récupérer le nombre d 'eneignes et les enseignes, camion et nbre camion pour les afficher dans la page

    data={
                'nbre_ens': nbre_ens,
                'L_enseigne': liste_enseigne,
                'camion' : camion,
                'liste_mag': liste_mag
        }
       
    return render_template('pages/selection_magasin.jinja',**data)
    

 #******************************************************************************************************VALIDER les MAGASINS CHOISIS**********************************************************       
@app.route('/valider_magasins', methods=['get','post'])
def valider_magasins():
    #camion_coche=request.form.getlist('liste_camion')
    list_camion_mat=con.execute(text("call liste_camion()")).fetchall()
    mag_coche=request.form.getlist('mag')
    rolls=request.form.getlist('rolls')
    palette=request.form.getlist('palette')
    nbre_rolls,nbre_pal=[],[]
    cpt=len(rolls)
    for i in range(cpt):
        if not (rolls[i]=='' and palette[i]==''):
            nbre_rolls.append(rolls[i])
            nbre_pal.append(palette[i])
            #nbre_boxe.append(box[i])
            print("magsiiiiiiiin","rolls",rolls[i],'palette',palette[i])
    date=request.form['date']    
    
    #/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_//_/_/_EXTRAIRE LES MAGASINS A LIVRER DU FICHIER EXCEL/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/
    mag_jour_casino = pd.read_excel('D:\\PerrenotStage\\alimentation_tables\\DocumentExploitation.xlsx', sheet_name=0, usecols=[7,9,10,11])
    mag_jour_casino.rename(columns={'Lib Mag':'magasin_adresse', 'H Mag':'magasin_heure_liv','Imm Mag': 'magasin_code', 'Rolls': 'nbre_rolls'}, inplace=True)
    mag_jour_casino=mag_jour_casino.groupby(['magasin_code','magasin_heure_liv','magasin_adresse' ])['nbre_rolls'].sum()
    mag_jour_casino=mag_jour_casino.reset_index()
    magasin_id        =[]
    magasin_Nexistants=[]
    mag_emb=[]
    casino_enseigne_id=pd.read_sql_query("select enseigne_id as ens_id from enseigne where enseigne_intitulé='CASINO' ", engine)['ens_id']
    mag_jour_casino['enseigne_id']=casino_enseigne_id[0]
    requete_mag_id="select magasin_id as id from magasin where magasin_code='%s' and enseigne_id='%s'"  
    for i in range(mag_jour_casino.shape[0]):
        mag_cd  =mag_jour_casino.iloc[i,0]
        ens_id  =mag_jour_casino.iloc[i,4]
        nbre_rol=mag_jour_casino.iloc[i,3]
        heur_liv=mag_jour_casino.iloc[i,1]
        mag_ad  =mag_jour_casino.iloc[i,2]
        if "EMB" in mag_cd:
            mag_emb.append(i)
        else:  # ne pas selectionner les magasins qui commencent par EMB
            mag_id=pd.read_sql_query(requete_mag_id %(mag_cd,ens_id), engine)['id']
            if  mag_id.empty:
                magasin_Nexistants.append((mag_cd,mag_ad,heur_liv))
                con.execute(text("insert into magasin (magasin_code, enseigne_id, magasin_heure_livr, magasin_adresse) values (:mag_code,:casino_enseigne_id, :heur_liv, :mag_ad)"), {'mag_code': mag_cd, 'casino_enseigne_id':int(casino_enseigne_id[0]),'heur_liv':heur_liv,'mag_ad':mag_ad})
            con.execute(text("insert into magasin_journalier (mag_id, nbre_rolls, date, magasin_code) values (:mag_id, :nbre_rolls, :date, :mag_code) on duplicate key update nbre_rolls=:nbre_rolls"), {'mag_id':int(mag_id[0]),'nbre_rolls':float(nbre_rol),'date':date,'mag_code': mag_cd})
            magasin_id.append(mag_id[0]) 
    if mag_emb:
        for i in range(len(mag_emb)):
            mag_jour_casino.drop(i,inplace=True)        
    mag_jour_casino['magasin_id']=magasin_id   
            
    #/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_//_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_//_//__/_/_/_/_/_/_/_/_/FIN/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/   

    # enregistrer les magasin cochés dans la table magasin journalier
    requete_mag_jour_code='select magasin_code from magasin where magasin_id=:magasin_id'     
       
    for j in range(len(nbre_rolls)):
        print("rolls",nbre_rolls[j],"palette",nbre_pal[j], "magasins", mag_coche[j])
        mag_code=con.execute(text(requete_mag_jour_code),{'magasin_id': mag_coche[j]}).fetchone()
        con.execute(text("insert into magasin_journalier (mag_id, nbre_rolls, nbre_pal, magasin_code, date) values(:mag_id, :nbre_rolls, :nbre_pal,  :magasin_code, :date) on duplicate key update nbre_rolls=:nbre_rolls and nbre_pal=:nbre_pal "), {'mag_id':mag_coche[j], 'nbre_rolls': nbre_rolls[j], 'nbre_pal': nbre_pal[j], 'magasin_code':mag_code[0], 'date':date,'nbre_rolls': nbre_rolls[j], 'nbre_pal': nbre_pal[j]})
        
    excel=request.form['fichier_excel']
    #récupérer le nombre de magains à livrer (sont stockés dans la table magasin_journalier)
    requete_nbre_mag='select count(*) from magasin_journalier where date=:date'
    nbre_mag=con.execute(text(requete_nbre_mag), {'date':date}).fetchone()[0]

    #récupérer les info des magasins à livrer 
    requete_mag_code='select magasin_journalier.magasin_code,nbre_rolls,nbre_pal,nbre_boxe, magasin_heure_livr, magasin_id from magasin_journalier join magasin on magasin.magasin_id =magasin_journalier.mag_id where magasin_journalier.date=:date'
    #requete_mag_code='select magasin_journalier.magasin_code,nbre_rolls,nbre_pal,nbre_boxe, magasin_heure_livr from magasin_journalier join magasin on magasin.magasin_id =magasin_journalier.mag_id'
  
    #mag_code=con.execute(text(requete_mag_code), {'date':date}).fetchall()
    mag_code=con.execute(text(requete_mag_code),{'date': date}).fetchall()

    #récupérer la liste des camion cochés
    camion=request.form.getlist('liste_camion')
    nbre_cam_ajout=round(len(camion)/3)
    print("liste completeeeeeeeeeeeeeeeeeeeeee camion",list_camion_mat)        
    
    requete_camion="select camion_mat, camion_cap, camion_id from camion where camion_mat in :camion"
    liste_camion=con.execute(text(requete_camion),{'camion':camion}).fetchall()
    #nbre_camion=len([row[0] for row in liste_camion])
    #récupérer la liste des chauffeurs dispo
    requete_chauffeur='call liste_chauffeur()'#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++test sur la date de livraison pas date d aujourdhui+++++++++++
    chauffeur=con.execute(text(requete_chauffeur)).fetchall()
    #liste_chauffeur = [row[0] for row in chauffeur]
    
    # données à envoyer a la page valider_tournée
    data={
                'nbre_mag': nbre_mag,
                'mag_code': mag_code,
                'chauffeur': chauffeur,
                'liste_camion':liste_camion,
                'date_tour':date, 
                'nbre_mag_Nexistant':len(magasin_Nexistants),
                'magasin_Nexistants':magasin_Nexistants,
                'list_camion_mat':list_camion_mat,
                'nbre_cam_ajout':nbre_cam_ajout
            }
    print()
    if   len(magasin_Nexistants)==0:     
        return render_template('pages/valider_tournee.html', **data)
    else:
        #flash('les magasins suivants:'magasin_Nexistants, 'danger') 
        mag_nExist="Erreur, les magasins suivant"+",".join(magasin_Nexistants)+" n'éxistaient pas et ont été ajoutés"
        flash(str(mag_nExist), 'danger')
        #return render_template('pages/valider_tournee.html', **data, return_msg={'msg':u'mag_nExist', 'type':u'danger'})
        return render_template('pages/valider_tournee.html', **data)
    
   
    
#*************************************************************************************************Identification***************************************************************        
@app.route('/authentification', methods=['post', 'get'])
def identification():
    pseudo=''
    nom=''
    prenom=''
    data={
            'nom': nom ,
            'prenom': prenom,
            'pseudo':pseudo
        }
    if request.method== 'POST':
        
        mot_de_pass=request.form['mdp']
        mot_de_pass=hashlib.sha1(str.encode(mot_de_pass)).hexdigest() # crypter le mot de passe tapé et le comparer avec celui qui est enregitré dans la BDD
        pseudo=request.form['pseudo']
        
        requete_role="select role_id as id from utilisateur where utilisateur_pseudo=:pseudo and utilisateur_MDP=:pass"
        requete_nom="select utilisateur_nom as nom from utilisateur where utilisateur_pseudo=:pseudo and utilisateur_MDP=:pass"
        requete_prenom= "select utilisateur_prenom as prenom from utilisateur where utilisateur_pseudo=:pseudo and utilisateur_MDP=:pass" 
              
        role=con.execute(text(requete_role),{'pass':mot_de_pass, 'pseudo':pseudo}).fetchone()
        nom=con.execute(text(requete_nom),{'pass':mot_de_pass, 'pseudo':pseudo}).fetchone()
        prenom=con.execute(text(requete_prenom),{'pass':mot_de_pass, 'pseudo':pseudo}).fetchone()
        data['pseudo']=pseudo
        data['nom']=nom
        data['prenom']=prenom
        
        if role is None: 
            flash(' pseudo et mot de passe ne correspondent pas, Veuillez vérifier votre saisie','danger')
            return render_template('pages/index1.html',**data)
            
        elif role[0]==1:
            return render_template('pages/accueil_admin.html',**data)
        
        elif role[0]==2:
            return render_template('pages/accueil_agent.html',**data)
    return render_template('pages/accueil_admin.html',**data)    
            
        
            

#**********************************************************************************changement MDP********************************************************************************      

    #return render_template('pages/index1.html',**data)
        
@app.route('/changement_mdp', methods=['post'])
def change_mdp():
    # connexion BDD
    pseudo=''
    nom=''
    prenom=''
    data={
            'nom': nom ,
            'prenom': prenom,
            'pseudo':pseudo
        }
    if request.method== 'POST':
        
        mot_de_pass=request.form['mdp']
        mot_de_pass=hashlib.sha1(str.encode(mot_de_pass)).hexdigest() # crypter le mot de passe tapé et le comparer avec celui qui est enregitré dans la BDD
        pseudo=request.form['pseudo']
        
        requete_role="select role_id as id from utilisateur where utilisateur_pseudo=:pseudo and utilisateur_MDP=:pass"
        requete_nom="select utilisateur_nom as nom from utilisateur where utilisateur_pseudo=:pseudo and utilisateur_MDP=:pass"
        requete_prenom= "select utilisateur_prenom as prenom from utilisateur where utilisateur_pseudo=:pseudo and utilisateur_MDP=:pass" 

              
        role=con.execute(text(requete_role),{'pass':mot_de_pass, 'pseudo':pseudo}).fetchone()
        nom=con.execute(text(requete_nom),{'pass':mot_de_pass, 'pseudo':pseudo}).fetchone()
        prenom=con.execute(text(requete_prenom),{'pass':mot_de_pass, 'pseudo':pseudo}).fetchone()
        
               
        data['pseudo']=pseudo
        
        if role is None: 
            flash('ce pseudo n existe pas, veuillez vérifier votre saisie', 'danger')
            return 'pseudo ou mot de passe ne sont pas corrects'
            
        elif role[0]==1:    
            
            return render_template('pages/accueil_admin.html',**data)
            
        else:
            return "bonjour agent d exploitation"       


if __name__=='__main__':
     app.run(debug=True, port=3000)