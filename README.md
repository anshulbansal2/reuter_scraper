# Thomson Reuters Site Scraper

https://apac1.apps.cp.thomsonreuters.com




#### Project Build:

    git clone git@github.com:anshulbansal2/reuter_scraper.git
    cd reuter_scraper
    docker build  -t reuter_scraper:latest -f Dockerfile .
    
#### Run ISIN producer:
    
    docker run -it --rm --name reuter_scraper --net='host' -e ENV=prod -t reuter_scraper:latest sh 
    -c "python scraper/isin_producer.py"
    
#### Run Scraper:

    docker run -it --rm --name reuter_scraper --net='host' -e ENV=prod -t reuter_scraper:latest sh -c "python scraper/main.py [userid] [password]" 
    

#### Local run:
    # Below will run docker for local dynamodb and local sqs  
        docker-compose up 
    
    # Produce isin to local sqs
        docker run -it --rm --name reuter_scraper --net='host' -e ENV=local -t reuter_scraper:latest sh -c "python scraper/isin_producer.py"
    
    # Consume and write scraper APIs response to local dynamodb
        docker run -it --rm --name reuter_scraper --net='host' -e ENV=local -t reuter_scraper:latest sh -c "python scraper/main.py [userid] [password]" 
    
        
#### APIs scraped:
    GetEstimateDetails:
        https://apac1.apps.cp.thomsonreuters.com/Apps/RecommendationTPApp/1.10.8/GetEstimateDetails'
             