export function setupGsap() {
    gsap.registerPlugin(MotionPathPlugin);
    // gsap.to("#train1", { rotation: 180 });
    // const circle = document.getElementById('movingCircle');
    // const path = document.getElementById('block1');
    // const moveBtn = document.getElementById('moveBtn');
    // const g1615 = document.getElementById('svg_12787');
    // let anim;
    // let isForward = true;
    //
    // // Set initial position at path start
    // const startPoint = path.getPointAtLength(0);
    // const endPoint = path.getPointAtLength(1);
    // console.log(startPoint, endPoint);
    // gsap.set(circle, {
    //     attr: {cx: startPoint.x, cy: startPoint.y}
    // });
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

// function getInitialLocation(initialBlock) {
//     const [pathId, startEnd] = initialLocationMap[initialBlock];
//     const path = document.getElementById(pathId);
//     return path.getPointAtLength(startEnd ? path.getTotalLength() : 0);
// }

function setSwitchState(switchId, state) {
    const rotation = switchStates[switchId][state];
    return gsap.to('#sw' + switchId, {duration: 0.5, rotation: rotation, transformOrigin: "90% 90%"});
}

function setTrainToLocation(trainId, initialBlock) {
    // const elem = document.getElementById(trainId);
    // const train = elem.getBoundingClientRect();
    const [pathIdHash, startEnd] = initialLocationMap[initialBlock];
    const trainIdHash = '#' + trainId;
    // gsap.set('#' + trainId, { x: xx + location.x - (train.width / 2), y: yy + location.y - (train.height / 2) });
    return gsap.to(trainIdHash, {
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

export function createAnimation(actions, initialState) {
    const element = document.getElementById("svg_container");
    var rect = element.getBoundingClientRect();

    var tl = gsap.timeline();

    // Move trains to their initial states
    const train1InitialBlock = initialState[0];
    const train2InitialBlock = initialState[2];
    tl.add(setTrainToLocation("train1", train1InitialBlock));
    tl.add(setTrainToLocation("train2", train2InitialBlock));

    // tl.delay(0.5);
    // Set initial switch states
    const initialSwitchStates = [0, 0, 0, 0];
    initialSwitchStates.forEach((state, switchId) => {
        tl.add(setSwitchState(switchId, state));
    });

    // tl.add(setSwitchState(3, 1));
    // tl.to(g1615, {duration: 1, rotation: 30, transformOrigin: "90% 90%"});
    // tl.to(g1615, {duration: 1, rotation: 0, transformOrigin: "90% 90%"});
    //tl.to(g1615, {duration: 1, rotation: 0, transformOrigin: "90% 90%"});
    // tl.to(circle, {
    //     motionPath: {
    //         path: "#block1",
    //         align: "#block1",
    //         alignOrigin: [0.5, 0.5],
    //         autoRotate: true,
    //         start: 0,
    //     },
    //     duration: 2,
    //     ease: "none"
    // });
    // tl.to(circle, {
    //     motionPath: {
    //         path: "#path1614",
    //         align: "#path1614",
    //         alignOrigin: [0.5, 0.5],
    //         autoRotate: true,
    //         start: isForward ? 0 : 1,
    //         end: isForward ? 1 : 0
    //     },
    //     duration: 2,
    //     ease: "none"
    // });
    return tl;
}
