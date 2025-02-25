import React from "react"
import * as ReactDOMClient from "react-dom/client"
import App from "./App"

const root = ReactDOMClient.createRoot(document.getElementById("root"));
class Main extends React.Component{
    render(){
        return(
            <App />
        )
    }
}

root.render(<Main />)
