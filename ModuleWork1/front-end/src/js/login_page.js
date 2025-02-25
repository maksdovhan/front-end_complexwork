import React from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import "../css/pagestyles.css";

class LoginPage extends React.Component {
    constructor(props) {
        super(props)
        this.state = {username: "", password: ""}
        this.LoginUser = this.LoginUser.bind(this)
    }

    render() {
        return (
            <>
                <div className="login_form_container">
                    <div className="main_info_login">
                        <span className="line">MaxCut ✂️</span>
                        <span className="line">Сервіс для скорочення посилань 🔗</span>
                    </div>
                    <div className="login_form">
                        <input type="text" className="input_user" placeholder="Ім'я користувача"
                            onChange={(e) => this.setState({username: e.target.value})}/>
                        <input type="password" className="input_password" placeholder="Пароль"
                            onChange={(e) => this.setState({password: e.target.value})}/>
                        <button className="enter_account" onClick={() => {this.LoginUser()}}>Увійти</button>
                        <button className="have_account" onClick={() => this.props.navigate("/register_user")}>Створити акаунт</button>
                    </div>
                </div>
                <footer>
                    <br/>Front-end сервісу створив Довгань Максим, студент групи ІО-24 <br/>
                    The front-end of the service was created by Dovhan Maksym, a student of the IO-24 group
                </footer>
            </>
        )
    }

    async LoginUser() {
        const { username, password } = this.state;
        try {
            const response = await axios.post(
                "http://localhost:8000/api/login",
                new URLSearchParams({username: username, password: password, scope: "", client_id: "", client_secret: "",}),
                {
                    headers: {"Content-Type": "application/x-www-form-urlencoded"}
                }
            );
            const token = response.data.access_token;
            localStorage.setItem("token", token);
            alert(`Вхід в акаунт ${username} виконано`);
            this.props.navigate("/link_shortener");
        }
        catch (error) {
            alert("Неправильний логін або пароль!");
        }
    }
}

function withNavigation(Component) {
    return function (props) {
        const navigate = useNavigate();
        return <Component {...props} navigate={navigate}/>;
    };
}

export default withNavigation(LoginPage);
