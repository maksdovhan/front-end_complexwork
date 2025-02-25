import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import LoginPage from "./js/login_page";
import RegisterPage from "./js/register_page";
import LinkshortenerPage from "./js/linkshortener_page";
import ShortenedlinksPage from "./js/shortenedlinks_page";

function App() {
    return (
        <Router>
            <Routes>
                <Route path="/" element={<LoginPage />} />
                <Route path="/register_user" element={<RegisterPage />} />
                <Route path="/link_shortener" element={<LinkshortenerPage />} />
                <Route path="/shortened_links" element={<ShortenedlinksPage />} />
            </Routes>
        </Router>
    );
}

export default App;
