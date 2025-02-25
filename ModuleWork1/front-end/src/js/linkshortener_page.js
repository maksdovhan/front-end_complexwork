import React from "react";
import axios from 'axios';
import { useNavigate } from "react-router-dom";

class LinkPage extends React.Component {
    constructor(props) {
        super(props)
        this.state = {url: "", short_link: "",}
        this.ShortLink = this.ShortLink.bind(this);
    }

    render() {
        return (
            <div className="shortener_link_container">
                <div className="main_info_shortener">
                    <div className="logo_info">
                        <span className="line">MaxCut ✂️<br/></span>
                        <span className="line">Сервіс для скорочення посилань 🔗</span>
                    </div>
                </div>
                <div className="shortener_form">
                    <h1>Будь ласка, введіть посилання, яке необхідно скоротити</h1>
                    <div className="input_url"><input type="text" className="url"
                        placeholder="Посилання для скорочення"onChange={(e) => this.setState({url: e.target.value})}/>
                    </div>
                    {this.state.shortLink && 
                        (<div className="new_short_url">
                            <p>Сформоване скорочене посилання: <br/> <br/><a href={`http://localhost:8000/${this.state.shortLink}`} target="_blank"
                                rel="noopener noreferrer">{`http://localhost:8000/${this.state.shortLink}`}</a>
                            </p>
                        </div>
                    )}
                    <div className="short_buttons">
                        <button className="short_url" onClick={() => {this.ShortLink()}}>Скоротити</button>
                        <button className="shortened_url" onClick={() => this.props.navigate('/shortened_links')}>Скорочені посилання</button>
                    </div>
                </div>
            </div>
        )
    }

    async ShortLink() {
        const {url} = this.state;
        const token = localStorage.getItem("token");
        if (!token) {
            alert("Виконайте вхід ще раз");
            return;
        }
        try {
            const response = await axios.post("http://localhost:8000/api/me/urls", { url: url }, {
                headers: {"Authorization": `Bearer ${token}`, "Content-Type": "application/json",},
            });
            this.setState({shortLink: response.data.short});
        }
        catch (error) {
            alert("Неправильний формат посилання!")
            this.setState({shortLink: ""});
        }
    }
}

function withNavigation(Component) {
    return function (props) {
        const navigate = useNavigate();
        return <Component {...props} navigate={navigate}/>;
    };
}

export default withNavigation(LinkPage);
