import {setupGsap, loadTrainTrackSVG, createAnimation} from './anim.js';
import { getInstructions } from './api.js';

const inputVectorRegex = /^[0-5]{1},[0-5]{1},[0-5]{1},[0-5]{1},[0-1]{1},[0-1]{1},[0-1]{1},[0-1]{1}$/;

loadTrainTrackSVG();
setupGsap();
let anim = null;

function validateInput(inputVector) {
    return inputVector.match(inputVectorRegex) !== null;
}

function getInputState() {
    return document.getElementById("circuit-state").value
}

function setButtonDisable(disable) {
    var element = document.getElementById("go");
    if (disable) {
        element.classList.add("cursor-not-allowed");
    } else {
        element.classList.remove("cursor-not-allowed");
    }
    element.disabled = disable;
}

function animFinished() {
    setButtonDisable(false);
}

function animate(actions, initialState) {
    if (anim) anim.kill();
    anim = createAnimation(actions, initialState, animFinished);
    anim.play();
}

document.getElementById('go').addEventListener('click', function () {
    // Get input and validate
    const initialStateAsString = getInputState();
    if (!validateInput(initialStateAsString)) {
        alert("Please enter a valid input");
    }

    // Call the backend to get the actions
    const initialState = initialStateAsString.split(',').map(value => parseInt(value));
    getInstructions(initialState).then(
        function(actions) {
            setButtonDisable(true);
            animate(actions, initialState);
        },
        function(error) { alert("Error from backend: " + error); }
    );
});

