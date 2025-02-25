import React, { Component } from "react";
import axios from "axios";

class ListLinkPage extends Component {
    constructor(props) {
        super(props);
        this.state = {links: [], redirects: {}, error: null};
    }

    componentDidMount() {
        this.fetchLinks();
    }

    async fetchLinks() {
        const token = localStorage.getItem('token');
        const links = [];
        const redirects = {};
        let page = 1;

        try {
            while (true) {
                const response = await axios.get(`http://localhost:8000/api/me/urls?page=${page}`, {
                    headers: {Authorization: `Bearer ${token}`,},
                });
                const currentLinks = response.data;
                if (currentLinks.length === 0) break;
                links.push(...currentLinks);
                page++;
            }

            for (let link of links) {
                const redirectResponse = await axios.get(`http://localhost:8000/api/me/links/${link.short}/redirects`, {
                    headers: {Authorization: `Bearer ${token}`,},
                });
                redirects[link.short] = redirectResponse.data;
            }
            this.setState({ links, redirects, error: null});
        }
        catch (error) {
            this.setState({error: "Виникла помилка"});
        }
    }

    render() {
        const { links, redirects, error } = this.state;

        if (error) {
            return <div>{error}</div>;
        }

        return (
            <div className="shortened_links_container">
                <div className="main_info_shortened">
                    <div className="logo">MaxCut ✂️</div>
                    <div className="slogan">Сервіс для скорочення посилань 🔗</div>
                </div>
                <h1>Список скорочених вами посилань</h1>
                <div className="shortened_links_list">
                    <div className="shortened_links_header">
                        <div className="list_cell">Оригінальне посилання</div>
                        <div className="list_cell">Скорочене посилання</div>
                        <div className="list_cell">Час скорочення</div>
                        <div className="list_cell">Кількість переходів</div>
                        <div className="list_cell">Час переходів</div>
                    </div>

                    {links.map((link) => (
                        <div key={link.short} className="list_row">
                            <div className="list_cell">
                                <a href={link.url} target="_blank" rel="noopener noreferrer">{link.url}</a>
                            </div>
                            <div className="list_cell">
                                <a href={`http://localhost:8000/${link.short}`} target="_blank" rel="noopener noreferrer">
                                    {`http://localhost:8000/${link.short}`}
                                </a>
                            </div>
                            <div className="list_cell">
                                {new Date(link.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}, {" "}
                                {new Date(link.created_at).toLocaleDateString()}
                            </div>
                            <div className="list_cell">{link.redirects}</div>
                            <div className="list_cell">
                                {redirects[link.short] && redirects[link.short].length > 0 ? (
                                    redirects[link.short].map((timestamp, index) => (
                                    <div key={index}>
                                        {new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })},{" "}
                                        {new Date(timestamp).toLocaleDateString()}
                                    </div>
                                    ))) : (<span>-</span>)
                                }
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        );
    }
}

export default ListLinkPage;
