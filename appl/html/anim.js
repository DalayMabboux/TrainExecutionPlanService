export function setupGsap() {
    gsap.registerPlugin(MotionPathPlugin);
}

export function loadTrainTrackSVG() {
    var request = new XMLHttpRequest();
    request.open("GET", "traintrack.svg", true);
    request.onload = function() {
        if (request.status >= 200 && request.status < 400) {
            var container = document.getElementById("svg_container");
            container.insertAdjacentHTML("beforeend", request.responseText);
        }
    };
    request.onerror = function() {
        console.error("Error: " + request.statusText);
    };
    request.send();
}

const initialLocationMap = {
    0: ['#p02', 0],
    1: ['#p12', 0],
    2: ['#p23', 0],
    3: ['#p23', 1],
    4: ['#p24', 1],
    5: ['#p25', 1]
}

const switchStates = {
    0: [95, 120],
    1: [31, 0],
    2: [-29, 5],
    3: [0, 36.5]
}

const trainMoveStates = {
    0: {
        0: 'p02',
        1: 'p50'
    },
    1: {
        0: 'p12',
        1: 'p51'
    },
    2: {
        0: 'p12',
        1: 'p51'
    }
}

function getSwitchStateAnim(switchId, state) {
    const rotation = switchStates[switchId][state];
    return gsap.to('#sw' + switchId, {duration: 0.5, rotation: rotation, transformOrigin: "90% 90%"});
}

function getTrainToLocationAnim(trainId, initialBlock) {
    // const elem = document.getElementById(trainId);
    // const train = elem.getBoundingClientRect();
    const [pathIdHash, startEnd] = initialLocationMap[initialBlock];
    // gsap.set('#' + trainId, { x: xx + location.x - (train.width / 2), y: yy + location.y - (train.height / 2) });
    return gsap.to(trainId, {
        motionPath: {
            path: pathIdHash,
            align: pathIdHash,
            alignOrigin: [0.5, 0.5],
            autoRotate: true,
            start: startEnd ? undefined : 0,
            end: startEnd ? 1 : 0,
            // 0:
            // start: 0,
            // end: 0,
            //
            // 1:
            // start: undefined,
            // end: 1,
        },
        duration: 0,
        ease: "none"
    });
}

function calculateNewBlock(currentBlock, isForward, state) {
    switch (currentBlock) {
        case 0:
        case 1:
            return isForward ? 2 : 5;
        case 2:
            if (isForward) {
                if (!state[6]) return 5;
                return !state[7] ? 4 : 3;
            }
            return !state[5] ? 0 : 1;
        case 3:
        case 4:
            return isForward ? -1 : 2;
        case 5:
            return isForward ? (!state[4] ? 0 : 1) : 2;
    }
}

function getPath(isForward, currentBlock, newBlock) {
    // if (!isForward && (currentBlock === 0 || currentBlock === 1)) {
    //     return  '#p' + (isForward ? ('' + newBlock + currentBlock) : ('' + currentBlock + newBlock));
    // } else {
    // }
    return  '#p' + (isForward ? ('' + currentBlock + newBlock) :  ('' + newBlock + currentBlock));
}

function getTrainAnim(action, state) {
    const trainNr = action.includes('1') ? 1 : 2;
    const trainIdx = trainNr === 1 ? 0 : 1;
    const currentBlock = state[trainIdx];
    const isForward = action.endsWith('forward');
    const newBlock = calculateNewBlock(currentBlock, isForward, state);
    const path = getPath(isForward, currentBlock, newBlock);
    state[trainIdx] = newBlock;
    return [gsap.to('#train' + trainNr, {
        motionPath: {
            path: path,
            align: path,
            alignOrigin: [0.5, 0.5],
            autoRotate: true,
            start: isForward ? 0 : 1,
            end: isForward ? 1 : 0,
        },
        duration: 2,
        ease: "none"
    }), state];
}

function getSwitchAnim(action, switchStates) {
    switch (action) {
        case 'switch_0_straight':
            if (switchStates[4] === 1) {
                switchStates[4] = 0;
                return [getSwitchStateAnim(0, 0), switchStates];
            }
            break;
        case 'switch_0_diverging':
            if (switchStates[4] === 0) {
                switchStates[4] = 1;
                return [getSwitchStateAnim(0, 1), switchStates];
            }
            break;
        case 'switch_1_straight':
            if (switchStates[5] === 1) {
                switchStates[5] = 0;
                return [getSwitchStateAnim(1, 0), switchStates];
            }
            break;
        case 'switch_1_diverging':
            if (switchStates[5] === 0) {
                switchStates[5] = 1;
                return [getSwitchStateAnim(1, 1), switchStates];
            }
            break;
        case 'switch_2_straight':
            if (switchStates[6] === 1) {
                switchStates[6] = 0;
                return [getSwitchStateAnim(2, 0), switchStates];
            }
            break;
        case 'switch_2_diverging':
            if (switchStates[6] === 0) {
                switchStates[6] = 1;
                return [getSwitchStateAnim(2, 1), switchStates];
            }
            break;
        case 'switch_3_straight':
            if (switchStates[7] === 1) {
                switchStates[7] = 0;
                return [getSwitchStateAnim(3, 0), switchStates];
            }
            break;
        case 'switch_3_diverging':
            if (switchStates[7] === 0) {
                switchStates[7] = 1;
                return [getSwitchStateAnim(3, 1), switchStates];
            }
            break;
    }
    return [null, switchStates];
}

export function createAnimation(actions, state, finishedCallback) {
    const element = document.getElementById("svg_container");
    var rect = element.getBoundingClientRect();

    var tl = gsap.timeline({
        onComplete: finishedCallback,
    });

    // Move trains to their initial states
    const train1InitialBlock = state[0];
    const train2InitialBlock = state[1];
    tl.add(getTrainToLocationAnim("#train1", train1InitialBlock));
    tl.add(getTrainToLocationAnim("#train2", train2InitialBlock));

    tl.delay(0.5);

    state.slice(-4).forEach((state, switchId) => {
        tl.add(getSwitchStateAnim(switchId, state));
    });

    actions.forEach(action => {
        if (action.startsWith("train")) {
            let anim;
            [anim, state] = getTrainAnim(action, state);
            if (anim) tl.add(anim);
        } else {
            let anim;
            [anim, state] = getSwitchAnim(action, state);
            if (anim) tl.add(anim);
        }
    })
    return tl;
}