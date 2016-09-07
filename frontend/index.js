import "babel-polyfill";
import "whatwg-fetch";

import React from "react";
import {render} from "react-dom";

import Live from "./components/Live";


render(
    <Live />,
    document.getElementById("app")
);
