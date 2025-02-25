import React from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";

class RegisterPage extends React.Component {
    constructor(props) {
        super(props)
        this.state = {username: "", password1: "", password2: "", full_name: ""}
        this.RegisterNewUser = this.RegisterNewUser.bind(this)
    }

    render() {
        return(
            <div className="register_form_container">
                <div className="main_info_register">
                    <span className="line">MaxCut ✂️</span>
                    <span className="line">Створення облікового запису</span>
                </div>
                <div className="register_form">
                    <input type="text" className="user_nickname" placeholder="Псевдонім користувача"onChange={(e) => this.setState({username: e.target.value})}></input>
                    <input type="text" className="user_name" placeholder="Ім'я користувача" onChange={(e) => this.setState({full_name: e.target.value})}></input>
                    <input type="password" className="user_password" placeholder="Введіть пароль" onChange={(e) => this.setState({password1: e.target.value})}></input>
                    <input type="password" className="user_repeat_password" placeholder="Повторіть пароль" onChange={(e) => this.setState({password2: e.target.value})}></input>
                    <button className="register" onClick={() => {this.RegisterNewUser()}}>Створити акаунт</button>
                </div>
            </div>
        )
    }

    RegisterNewUser = async () => {
        const {username, password1, password2, full_name } = this.state;
        if (password1 === password2) {
            axios.post("http://localhost:8000/api/register", {username: username, password: password1, full_name: full_name,})
                .then(function (response) {
                    alert("Акаунт успішно створений!")
                })
                .catch(function (error) {
                    if (error.response.status===409) {
                        alert("Даний нікнейм зайнятий, будь ласка, введіть інший!")
                    }
                    if (error.response.status===422) {
                        alert("Дані введено некоректно!")
                    }
                });
        }
        else {
            alert("Паролі не співпадають! Будь ласка, спробуйте ще раз")
        }
    };
}

function withNavigation(Component) {
    return function (props) {
        const navigate = useNavigate();
        return <Component {...props} navigate={navigate}/>;
    };
}

export default withNavigation(RegisterPage);
