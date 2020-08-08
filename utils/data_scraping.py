#Importing the neccessary libraries
from bs4 import BeautifulSoup
import requests
import bs4
import shutil
import os
import pandas as pd

# fuction to download the images of parasites and it's the meta-data
def parasite_data(url, Phylum, Class):
    
    #make a common dir for datasets
    os.chdir("Dataset")
    base_url="https://www.cdc.gov/"
    
    #request the bs4 response from the net
    response=requests.get(url)
    print(response)
    soup = BeautifulSoup(response.content, 'html.parser')
    Genus=soup.find('div',attrs={'id':'sync-content'}).em.text.strip().split()[0]  #genus of the parasite
    print(Genus)
    #get the image_gallery tab 
    links=soup.find_all('a',class_='nav-link')
    for link in links:
        if link.text.startswith("Image"):
            p=link
    gallery_tab=p.get("href")
    image_gallery=soup.find('div',attrs={'id':gallery_tab[1:]})
    card_body=image_gallery.find('div',class_='card-body')
    
    #make dir of each genus
    if not os.path.isdir(f'{Genus}'):
        os.mkdir(Genus)
        
    #variable to store the data    
    Phylum_=[]
    Class_=[]
    Genus_=[]
    Image_name_=[]
    Image_url_=[]
    Image_info_=[] #e.g smear type
    multi=0 #to chech whether it has multi species
    
    #differentiate betwen different html strucures
    try:
        is_multi=card_body.div.div.div.div.div
        multi=1
    except:
        pass
    
    #if single species html site
    if multi==0:
        species_name=soup.find('div',attrs={'id':'sync-content'}).em.text.strip()
        # species_name="Iodamoeba buetschlii"

        for row in image_gallery.find_all('div',"row"):
            cols = row.find_all('div','card')

            for each_image in cols:
                img_info=each_image.div.text.strip("\n").split(':')[-1].strip()
                img_url=base_url+str(each_image.img.get("src"))
                img_name=each_image.img.get("title")
                if img_name is None:
                    img_name=img_url.split("/")[-1].strip()
                print(species_name)
                print(img_name)
                print(img_url)
                print(img_info)

                #storing the meta-data
                Phylum_.append(Phylum)
                Class_.append(Class)
                Genus_.append(Genus)
                Image_name_.append(img_name)
                Image_url_.append(img_url)
                Image_info_.append(img_info)
                print("--------------------------------------------------")

                #create dir for each species
                if not os.path.isdir(f"{Genus}/{species_name}"):
                    os.mkdir(f"{Genus}/{species_name}")

                #downloading the image in respective dir
                img_file = requests.get(img_url, stream=True)
                with open(f"{Genus}/{species_name}/{img_name}", 'wb') as out_file:
                    shutil.copyfileobj(img_file.raw, out_file)
       
    #If multi species html structure site    
    else:
        for each_species in card_body.children:
            if type(each_species)==bs4.element.Tag:
                section=each_species.find("div","card-body")
                print(section.em.text)
                species_name = section.em.text.strip()

                for row in image_gallery.find_all('div',"row"):
                    cols = row.find_all('div','card')

                    #Getting each image and it's data
                    for each_image in cols:
                        img_info=each_image.div.text.strip("\n").split(':')[-1].strip()
                        img_url=base_url+str(each_image.img.get("src"))
                        img_name=each_image.img.get("title")
                        if img_name is None:
                            img_name=img_url.split("/")[-1].strip()
                        print(species_name)
                        print(img_name)
                        print(img_url)
                        print(img_info)

                        #storing the meta-data
                        Phylum_.append(Phylum)
                        Class_.append(Class)
                        Genus_.append(Genus)
                        Image_name_.append(img_name)
                        Image_url_.append(img_url)
                        Image_info_.append(img_info)
                        print("--------------------------------------------------")

                        #create dir for each species
                        if not os.path.isdir(f"{Genus}/{species_name}"):
                            os.mkdir(f"{Genus}/{species_name}")

                        #downloading the image in respective dir
                        img_file = requests.get(img_url, stream=True)
                        with open(f"{Genus}/{species_name}/{img_name}", 'wb') as out_file:
                            shutil.copyfileobj(img_file.raw, out_file)
                        
    #converting the meta-data to csv file for easy accessibility
    df = pd.DataFrame(list(zip(Phylum_, Class_,Genus_,Image_name_,Image_info_,Image_url_)), 
               columns =['phylum', 'class', 'genus','image_name','image_info','image_url'])
    
    #saving the meta-data
    df.to_csv(f"{Genus}/{Genus}_mata_data.csv")
    # print(df.shape)
    os.chdir("../")
    return df

#To make a dir to store all the data     
if not os.path.isdir("Dataset"):
    os.mkdir("Dataset")
    
#url for parasite  e.g-> malaria
url='https://www.cdc.gov/dpdx/taeniasis/index.html'

Phylum="Platyhelminthes"
Class="Cestoda"
meta_data=parasite_data(url,Phylum,Class)

print(meta_data.shape)
print(print(meta_data.iloc[:5,:4]))
print("******************************************")



