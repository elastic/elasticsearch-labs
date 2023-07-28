import React, { Component, Fragment } from "react";

class Footer extends Component {
  render() {
    return (
        <footer>
            <div style={{ width:"100%", color: "white", textAlign: "center", fontSize: 12}}>
                <div>
                    <p>Elastic Demo Environment ||| <a href="https://www.elastic.co/legal/trademarks" target="_blank" rel="noopener noreferrer">Trademarks</a> | <a href="https://www.elastic.co/legal/terms-of-use" target="_blank" rel="noopener noreferrer">Terms of Use</a> | <a href="https://www.elastic.co/legal/privacy-statement" target="_blank" rel="noopener noreferrer">Privacy</a> | © 2023. Elasticsearch B.V. All Rights Reserved</p>
                </div>
                <div style= {{"display" : "flex", justifyContent: "center"}}>
                    <img
                        src="/tmdb-logo.svg"
                        alt=""
                        width="50" 
                    
                    /> 
                    <div style= {{marginLeft: "10px"}}>
                        Credits: This product uses the TMDB API but is not endorsed or certified by TMDB.
                    </div>
                </div>
            </div>
        </footer>
      
    );
  }
}

export default Footer;