# raw

##Using Deployment script


Quick Run:

    git clone git@github.com:anshulbansal2/reuter_scraper.git
    cd reuter_scraper
    docker build  -t reuter_scraper:latest -f Dockerfile .
    docker run -it --rm --name reuter_scraper -t reuter_scraper:latest sh -c "python scraper/main.py
     [pass user_id] [pass password]"
    
    
     