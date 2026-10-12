# Ancien import des licenciés depuis l'export CSV de la fédération.
# Usage : python scripts/legacy/import_licencies.py [fichier.csv]  (serveur lancé sur le port 8000)
import csv,json,os,sys,urllib.request,urllib.error
def conv(d):
    # jj/mm/aaaa -> aaaa-mm-jj
    if d=="" or d==None: return None
    p=d.split("/")
    return p[2]+"-"+p[1]+"-"+p[0]
def main():
    f=os.path.join(os.path.dirname(__file__),"licencies_exemple.csv")
    if len(sys.argv)>1: f=sys.argv[1]
    ok=0;dej=0;err=[]
    n=1
    for l in csv.DictReader(open(f,encoding="utf-8"),delimiter=";"):
        n=n+1
        try:
            a={"last_name":l["nom"].strip(),"first_name":l["prenom"].strip(),"birth_date":conv(l["date_naissance"].strip()),"sex":l["sexe"].strip(),"club":l["club"].strip() or None,"license_number":l["licence"].strip(),"medical_certificate_valid_until":conv(l["certificat_valide_jusqu"].strip())}
        except Exception as e:
            err.append("ligne "+str(n)+" : "+str(e)); continue
        r=urllib.request.Request("http://localhost:8000/athletes",data=json.dumps(a).encode("utf-8"),headers={"Content-Type":"application/json"},method="POST")
        try:
            urllib.request.urlopen(r); ok=ok+1
        except urllib.error.HTTPError as e:
            if e.code==409: dej=dej+1
            else: err.append("ligne "+str(n)+" : HTTP "+str(e.code))
    print("crees: "+str(ok))
    print("deja presents: "+str(dej))
    print("erreurs: "+str(len(err)))
    for e in err: print("  "+e)
if __name__=="__main__": main()
