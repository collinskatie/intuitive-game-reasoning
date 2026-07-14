var timeline = [];

/* init connection with pavlovia.org */
var pavlovia_init = {
  type: "pavlovia",
  command: "init",
};
timeline.push(pavlovia_init);

// capture info from Prolific
// help from: https://www.jspsych.org/overview/prolific/
var prolific_id = jsPsych.data.getURLVariable("PROLIFIC_PID");
var study_id = jsPsych.data.getURLVariable("STUDY_ID");
var session_id = jsPsych.data.getURLVariable("SESSION_ID");
// subj id help from: https://www.jspsych.org/7.0/overview/data/index.html
// generate a random subject ID with 15 characters
var subject_id = jsPsych.randomization.randomID(15);
jsPsych.data.addProperties({
  subject: subject_id,
  prolific_id: prolific_id,
  study_id: study_id,
  session_id: session_id,
});

var scales = {

  how_fun: ["The least fun  of this class of grid-based game", "Neutral", "The most fun of this class of grid-based game"],
};

generic_game_q = "the following questions are <i>not about this particular video</i> but <strong>this game overall, with these rules</strong> for two new reasonable human players."


var task_questions = {

  how_fun: {
    q_fmt: "<p>Now remember, " + generic_game_q + "</p>" + "How fun is this game?",
    instruct_fmt: "how fun the game would be to play",
  },
  advantage: {
    q_fmt: "Assuming two new random human players play reasonably -- if the game does not end in a draw, how likely is it that the first player is going to win (not draw), and how likely is a draw?",
    instruct_fmt:
      "how the game is likely to end in general: (1) assuming two new random human players play reasonably -- if the game does not end in a draw, how likely is it that the first player is going to win (not draw), and (2) how likely is a draw",
  },
};

var advantage_sliders = [

  {
    prompt: "<p>Now remember, " + generic_game_q + "<br><br></p>" + 
    "<p><strong>Assuming <i>two NEW random human players</i> play reasonably, if the game <i>does not end in a draw</i>, how likely is it that the first player is going to win (<i>not draw</i>)?" + "</strong></p><p>    </p>",
    name: "firstplayer_response",
    labels: [
      "First player definitely going to <strong>lose</strong>",
      "Equally likely to <strong>win or lose</strong>",
      "First player definitely going to <strong>win</strong>",
    ],
    required: true,
  },
  {
    prompt: "<p><strong>" + "Assuming both new human players play reasonably, how likely is the game to end in a draw?" + "</strong></p><p>    </p>",
    name: "draw_response",
    labels: ["Impossible to end in a draw", "Equally likely to end in a draw or not",
      "Definitely going to end in a draw",],
    required: true,
  },

];

var turing_test_slider = {
  prompt: "<p>The following questions are <strong>about this particular match</strong>:<br><br></p><p>How likely do you think it is that this match was <strong>played by two humans</strong> playing the game for the first time, <strong>or played by two computer bots</strong> designed to play like two humans playing this game for the first time?</p>",
  name: "turingtest",
  labels: [
    "Definitely two humans",
    "Equally likely to be two humans or two computers",
    "Definitely two computers",
  ],
  required: true,
}

var skill_sliders = [
  {
    prompt: "<p><strong>Out of 100 other new random players</strong>, where do you think the <span style='color:" + "blue" + ";'>BLUE</span> player (who played first in this match) would <strong>rank in skill</strong> for this game?</p>",
    name: "firstplayer_skill",
    labels: [
      "Better than 0 other players", 
      "Better than 50 other players", 
      "Better than all 100 other players",
    ],
    required: true,
  },
  {
    prompt: "<p><strong>Out of 100 other new random players</strong>, where do you think the <span style='color:" + "red" + ";'>RED</span> player (who played second in this match) would <strong>rank in skill</strong> for this game?</p>",
    name: "secondplayer_skill",
    labels: [
      "Better than 0 other players", 
      "Better than 50 other players", 
      "Better than all 100 other players",
    ],
    required: true,
  },

];

// pick a random condition for the subject at the start of the experiment
// help from: https://www.jspsych.org/overview/prolific/
// based on our total number of batches <--- note: can subset if we need to run some a few more

var num_batches = 5;

var conditions = Array.from(Array(num_batches).keys()); // help from: https://www.codegrepper.com/code-examples/javascript/javascript+create+list+of+numbers+1+to+n

var rem_conds = []
var conditions = conditions.filter((n) => !rem_conds.includes(n));
console.log("conditions: ", conditions);

var condition_num = jsPsych.randomization.sampleWithoutReplacement(
  conditions,
  1
)[0];


console.log("condition num: ", condition_num)

// official run off - debug mode
var official_run = true;

if (!official_run) {
  var min_seconds = 2
} else {
  var min_seconds = 60
}

// record the condition assignment
jsPsych.data.addProperties({
  condition: condition_num,
});

var stimuli_batch = batch_data[condition_num]//.slice(0, 1)
console.log(" batch: ", condition_num);
console.log("stimuli batch: ", stimuli_batch[0])
var task = stimuli_batch[0]["task"];

console.log(stimuli_batch)

// consent form help from: https://gitlab.pavlovia.org/beckerla/language-analysis/blob/master/html/language-analysis.js
// sample function that might be used to check if a subject has given consent to participate.
var check_consent = function (elem) {
  if (
    $("#consent_checkbox").is(":checked") &&
    $("#read_checkbox").is(":checked") &&
    $("#age_checkbox").is(":checked")
  ) {
    return true;
  } else {
    alert(
      "If you wish to participate, you must check the boxes in the Consent Form."
    );
    return false;
  }
  return false;
};
var consent = {
  type: "external-html",
  url: "consent.html",
  cont_btn: "start",
  check_fn: check_consent,
};
if (official_run) {
  timeline.push(consent);
}

console.log("label" + (1 + 1));

var num_show = stimuli_batch.length;

var progress_bar_increase = 1 / num_show;

var total_time = 25;
var base_rate = 13.5;
var bonus_rate = 15;

var base_pay = base_rate * (total_time / 60);
var bonus_pay = bonus_rate * (total_time / 60) - base_pay;

base_pay = parseFloat(base_pay).toFixed(2);
bonus_pay = parseFloat(bonus_pay).toFixed(2);

var condition_caveat = "";
var postq = "";
if (task.includes("fun")) {
  condition_caveat = "<p>We ask that you think about funness <i>with respect to this kind of game</i>; that is, games that involve players placing pieces on a grid.</p><p>You can define fun however you wish.</p>";
  postq = "";
}


var num_clear_clicks = 0;
var all_click_traces = [];
var ready_btn = "the SPACE bar"
var last_cell = ""
var selectedColor = ""

// Function to update hover effect
function updateHoverEffect(effect) {
  document.querySelectorAll('.cell').forEach(cell => {
    cell.classList.remove('hover-blue', 'hover-red', 'hover-green');
    if (effect) {
      cell.classList.add(effect);
    }
  });
}

var clickCounts = {};
var modifiedCells = new Set();
var noModifyCells = new Set();

var maxClicks = 5
var minClicks = maxClicks

function totalClicks(){ 
  return Object.values(clickCounts).reduce((sum, count) => sum + count, 0);
}

function getMoveNumber(moveHistory, row, col, currentMaxMoveShown) {
  // currentMaxMoveShown helps us make sure we don't reveal a "future" move early
  const move = moveHistory.find(m => m.row === row && m.col === col && m.moveNumber <= currentMaxMoveShown);
  return move ? move.moveNumber : '';
}




// persist over the examples for a single stimuli
var boardStates = []; 
var moveHistory = []; 
var gameStage = 0 // beginning = 0, middle = 1, end = 2

var readStimuli = {
  type: "html-keyboard-response",
  stimulus: function () {

    var task = jsPsych.timelineVariable("task");
    var board_rows = jsPsych.timelineVariable("board_rows");
    var board_cols = jsPsych.timelineVariable("board_cols");
    var win_conditions = jsPsych.timelineVariable("win_conditions");

    // var opener_txt = `<p><strong>In this game,</strong> imagine you are playing on a <strong>${board_rows} x ${board_cols} board</strong>.</p>`;
    var opener_txt = `<p>Two players are playing on a <strong>${board_rows} x ${board_cols} board</strong>.</p>`;

    var cond_txt =
      "<p>The rules for this game are that: <strong>" +
      win_conditions +
      "</strong></p>";

      var task_txt = 
      '<p>When you feel you understand the game (after at least ' + readTimePer + ' seconds have passed), press ready to start the video.</p>'

      var game_container = `
      <div id="container" style="text-align: center;">
        <div id="gameBoard" style="display: grid; justify-content: center;"></div>
      </div>`

    return opener_txt + cond_txt + task_txt +game_container ;
  },
  on_load: function () {

    gameStage = 0 

    console.log('boards before load: ', boardStates)
    boardStates = jsPsych.timelineVariable('boards')
    console.log('boards after load: ', boardStates)

    var rows = boardStates[0].length
    var cols = boardStates[0][0].length


    for (let i = 1; i < boardStates.length; i++) {
      for (let row = 0; row < rows; row++) {
        for (let col = 0; col < cols; col++) {
          if (boardStates[i][row][col] !== boardStates[i-1][row][col]) {
            moveHistory.push({row, col, moveNumber: i});
          }
        }
      }
  }


    // Function to cycle through board states
    setTimeout(() => {
      // Create and style the "What will happen next?" button
      const nextButton = document.createElement("button");
      nextButton.textContent = "Ready to watch!";
      nextButton.style.marginTop = "20px";
      nextButton.style.padding = "10px 20px";
      nextButton.style.fontSize = "16px";
      nextButton.style.backgroundColor = "#112242";
      nextButton.style.color = "white";
      nextButton.style.border = "none";
      nextButton.style.cursor = "pointer";
      nextButton.onclick = () => {
        jsPsych.finishTrial(); // End the trial
      };
      container.appendChild(nextButton);
    }, readTimePer * 1000);
  },
  on_finish: function () {
    console.log("read trial completed");
  }
}

// Track positions of moves
// var moveHistory = [];

// var moveTimePer = 2 //1.5

if (official_run){ 
  var moveTimePer = 2
}else{ 
  var moveTimePer = 0.1
}

let BASE_BLUE = "rgba(0, 0, 255, 0.7)"
let BASE_RED = "rgba(255, 0, 0, 0.7)"

var watchBoard = {
  type: "html-keyboard-response",
  stimulus: function () {

    var task = jsPsych.timelineVariable("task");
    var board_rows = jsPsych.timelineVariable("board_rows");
    var board_cols = jsPsych.timelineVariable("board_cols");
    var win_conditions = jsPsych.timelineVariable("win_conditions");

    // var opener_txt = `<p><strong>In this game,</strong> imagine you are playing on a <strong>${board_rows} x ${board_cols} board</strong>.</p>`;
    var opener_txt = `<p>Two players are playing on a <strong>${board_rows} x ${board_cols} board</strong>.</p>`;

    var cond_txt =
      "<p>The rules for this game are that: <strong>" +
      win_conditions +
      "</strong></p>";

      var task_txt = '<p>Here is a video of how the players played.</p>'
    var game_container = `
      <div id="container" style="text-align: center;">
        <div id="gameBoard" style="display: grid; justify-content: center;"></div>
      </div>`

    // Create a placeholder div for the game board
    return opener_txt + cond_txt + task_txt + game_container;
  },
  choices: jsPsych.NO_KEYS, // No input allowed initially
  trial_duration: null, // Trial ends manually with "Next" button
  on_load: function () {
    var rows = jsPsych.timelineVariable("board_rows");
    var cols = jsPsych.timelineVariable("board_cols");

    var predMoveIdxs = jsPsych.timelineVariable('pred_move_idxs')
    var predPlayerAtIdxs = jsPsych.timelineVariable('player_at_idx')

   

    if (gameStage == 0) {
      var startMove = 0
      var endMove = predMoveIdxs[0] - 1

    }else if (gameStage == 1){
      var startMove = predMoveIdxs[0] - 1
      var endMove = predMoveIdxs[1] - 1
      console.log("stage 1: ", startMove, endMove)
    }else{ 

      var startMove = predMoveIdxs[1] - 1
      var endMove = predMoveIdxs[2] - 1

    }

    console.log("starting moves: ", predMoveIdxs, startMove, endMove)

    console.log('boards before load: ', boardStates)
    //boardStates = jsPsych.timelineVariable('boards')
    // console.log('boards after load: ', boardStates)

    var currentIndex = startMove;
    var boardState = boardStates[currentIndex]

    console.log("current board state: ", boardState, currentIndex)

    const container = document.getElementById("container");
    const boardContainer = document.getElementById("gameBoard");

    // Calculate cell size based on `predictBoard` logic
    const maxWidth = window.innerWidth * 0.4;
    const maxHeight = window.innerHeight * 0.4;
    const cellSize = Math.min(maxWidth / cols, maxHeight / rows);


    // Apply consistent grid style
    boardContainer.style.gridTemplateColumns = `repeat(${cols}, ${cellSize}px)`;
    boardContainer.style.gridGap = "2px";

    
    // Function to render a specific board state
    function renderBoard(boardState, currentMaxMoveShown) {
      boardContainer.innerHTML = ""; // Clear previous board

      for (let row = 0; row < rows; row++) {
        for (let col = 0; col < cols; col++) {
          const cell = document.createElement('div');
          cell.id = `${row}-${col}`;
          cell.classList.add('cell');
          cell.style.width = `${cellSize}px`;
          cell.style.height = `${cellSize}px`;

          // Set cell color based on board state
          if (boardState[row] && boardState[row][col] === 1) {
            cell.style.backgroundColor = BASE_BLUE;
            cell.style.color = "white";
          } else if (boardState[row] && boardState[row][col] === 2) {
            cell.style.backgroundColor = BASE_RED;
            cell.style.color = "white";
          } else {
            cell.style.backgroundColor = "white";
          }

          const moveNumber = getMoveNumber(moveHistory, row, col, currentMaxMoveShown);
          if (moveNumber) {
            cell.textContent = moveNumber;
            cell.style.color = "black";
          }

          boardContainer.appendChild(cell);
        }
      }
    }


    function updateBoard() {
      console.log("going to render: ", boardStates, currentIndex)
      renderBoard(boardStates[currentIndex], currentIndex); // pass the move order as well
      
      console.log("current index: ", currentIndex, " end move: ", endMove)

      if (currentIndex ===endMove){ //boardStates.length) {
        console.log("clearing interval: ", endMove, gameStage)
        clearInterval(interval); // Stop updates after the last state

        const nextButton = document.createElement("button");
        nextButton.textContent = "Suggest the next move!"; //"What do you think should happen next?";
        //nextButton.textContent = "Predict the next move!"; //"What do you think should happen next?";

        nextButton.style.marginTop = "20px";
        nextButton.style.padding = "10px 20px";
        nextButton.style.fontSize = "16px";
        nextButton.style.backgroundColor = "#112242";
        nextButton.style.color = "white";
        nextButton.style.border = "none";
        nextButton.style.cursor = "pointer";
        nextButton.onclick = () => {
          jsPsych.finishTrial(); // End the trial
        };
        container.appendChild(nextButton);
      }
      currentIndex++;
    }

    // Initial render
    updateBoard();

    // update board at intervals matching with the move time
    var interval = setInterval(() => {
      console.log('interval: ', boardStates.length)
      if (currentIndex < boardStates.length) {
        updateBoard();
      }
    }, moveTimePer * 1000);
  },
  on_finish: function () {
    console.log("WatchBoard trial completed.");
  },
};

var readTimePer = 5

var suggestionForcedRespTime = 5


var simple_question_txt = ""
if (task.includes("fun")) {
  simple_question_txt = "a simple question"
} else {
  simple_question_txt = "two simple questions"
}

var instruction_images = ["tictactoe_certain.gif", "tictactoe_multi.gif", "tictactoe_two.gif"];
var preloadAll = {
    type: "preload",
    images: instruction_images,
    auto_preload: true,
    show_detailed_errors: true,
    max_load_time: 60000
};
timeline.push(preloadAll);


var instruction_pages = [
  "<p> Welcome! </p> <p> We are conducting an experiment to understand how people think about and play games. Your answers will be used to inform cognitive science and AI research. </p>" +
  "<p> This experiment should take approximately <strong>" +
  total_time +
  " minutes</strong>. </br></br> You will be compensated at a base rate of $" +
  base_rate + 
  "/hour with an optional bonus to bring the total up to a rate of $" + bonus_rate + "/hr if you try your best throughout the experiment to answer each question.</p>" +
  "<p>Please set the experiment to full screen.</p>",
  "<p> We take your compensation and time seriously! The email for the main experimenter is <strong>katiemc@mit.edu</strong>. </br></br> Please write this down now, and email us with your Prolific ID and the subject line <i>Human experiment compensation</i> if you have problems submitting this task, or if it takes much more time than expected. </p>",
  "<p>Please do <i>not</i> use any other Internet source or aid, including internet search, or chatbots — this experiment is designed to measure <i>how people think.</i></p><p>Unfortunately, if we find evidence that you did this, you may not receive the payment for this task.",
  "<p> In this experiment, you will read several short English descriptions of board games. You will watch a video of each game being played, and answer questions about each game.</p>" + 
   "<p>The rules of each game will vary, but each game involves placing pieces on a grid, similar to games like Connect 4, Gomoku (5-in-a-row), or Tic-Tac-Toe.</p>" + 
    
  "<p>In these videos, the players are two humans playing each other in the game for the first time.</p>", 
  "<p>Each video will <strong>freeze at three time points</strong>: once in the beginning, once in the middle, and once near the end of the game.</p>"+ 
  "<p>Note: moves in the video are played at a fixed time rate, not how long it took the actual player to make their move.</p>", 
  "<p>When the video freezes, you will be asked to suggest <strong>what a particular player should do next</strong> on an interactive version of the board.</p>",


  "<p>You will be given <strong>" + maxClicks + "</strong> clicks to indicate your predictions. You can click more than once on any open space." + 

  "<p><strong>Use your clicks to indicate how certain you are that a player should move to that location</strong>; the more clicks, the more confident you are that they should move there.</p>",

  "<p>For instance, if you are very confident that a player should move to a particular location, put all of your clicks in one cell, like this: <br><br><img src='tictactoe_certain.gif' style='width: 75%;'>",

  "<p>If you think the player should move in one of two spots, spread your clicks across both locations, like this (and add 1 where you think they should go if you had to choose one): <br><br><img src='tictactoe_two.gif' style='width: 75%;'>",

  "<p>If you are very unsure where they should play next, spread your clicks across any location you think is reasonable, like this: <br><br><img src='tictactoe_multi.gif' style='width: 75%;'>",

  "<p>You can clear your clicks if you would like to restart.</p>" + 
  "<p>You must spend at least " + suggestionForcedRespTime + " seconds on your suggested responses beore being able to continue. The SUBMIT button will activate when you are permitted to submit your clicks.</p>" ,
  
  
  
  "<p>After you have made your predictions at each of the three stages of the game, you will be shown the rest of the match.</p>" + 

    "<p>You will then be asked <strong>how <i>skilled</i> you think each opponent is</strong> from the match you just saw.</p>", 
  
  "<p>You will <strong><i>also</i> be asked</strong> to answer some questions <strong>about the game overall</strong> (<i>NOT</i> just the match you watched):</p>" + 
  task_questions[task]["q_fmt"] +
  "</strong></p>" +
  "<p>We emphasize that <strong>these questions are not about this particular match video, but this game overall</strong> with the specific rules (and any two new reasonable human players).</p>" + "<p>You should treat your experience with your the video'd match as only an example of how the game works.</p>" + 
  "<p>You will answer all questions by <strong>dragging a slider.</strong></p>" +
  condition_caveat,


  "<p>Before you start watching the video for each game, you will have <i>as much time as you want to think about the game and its rules</i>.</p><p>You must spend at least " + readTimePer + " seconds thinking about each game.</p>",



  "<p>Some games may be easier to reason about than other games. Please try your best!</p>",
]


instruction_pages.push(
  "<p> You will see a total of <strong>" +
  num_show +
  " games</strong>, with one round per game.</p>"
);

instruction_pages.push(
  '<p> When you are ready, please click <strong>"Next"</strong> to complete a quick comprehension check, before moving on to the experiment. </p>' +
  "<p> Please make sure to window size is in full screen to properly view the questions. </p>"
);

var instructions = {
  type: "instructions",
  pages: instruction_pages,
  show_clickable_nav: true,
};

var correct_task_description =
  "Read descriptions of various games and determine " +
  task_questions[task]["instruct_fmt"] +
  ".";

var correct_response_indicator = "Dragging a slider.";
var correct_scratchpad_resp = "For every game, but it is optional.";
var chatbot_affirm = "I affirm that I will not use any other Internet source or aid, including internet search, or chatbots."

var correct_main_task_description = "Watching videos of players' gameplay and indicating where you think they should move."
var  correct_response_indicator_pred = "To suggest what a player should do next."

var comprehension_check = {
  type: "survey-multi-choice",
  preamble: [
    "<p align='center'>Check your knowledge before you begin. If you don't know the answers, don't worry; we will show you the instructions again.</p>",
  ],
  questions: [
    {
      prompt: "What will you be asked to do in this task?",
      options: [
        
        "Design new versions of games and then play them.",
        correct_main_task_description,
        "See pictures of in-progress games and predict the winner.",
      ],
      required: true,
    },


    {
      prompt: "What will you be asked about for each scenario?",
      options: [
        "To predict what a player will do next.",
        correct_response_indicator_pred,
      ],
      required: true,
    },


    {
      prompt: "What is one of the judgements you will be asked about for each game?",
      options: [
        correct_task_description,
        "Predict who will win the next game.",
        "Determine how fun the players would have thought the game was.",
      ],
      required: true,
    },

    

    {
      prompt: "Do you affirm that you will not use any other Internet source or aid, including internet search, or chatbots?",
      options: [
        "I affirm that I will not use any other Internet source or aid, including internet search, or chatbots.",
        "No, I do not affirm that I will not use any other Internet source or aid, including internet search, or chatbots. I might use them.",
      ],
      required: true,
    },

  ],
  on_finish: function (data) {
    var responses = data.response;
    if (
      responses["Q0"] == correct_main_task_description &&
      responses["Q1"] == correct_response_indicator_pred &&
      responses["Q2"] == correct_task_description &&
      responses["Q3"] == chatbot_affirm
    ) {
      familiarization_check_correct = true;
    } else {
      familiarization_check_correct = false;
    }
  },
};

var familiarization_timeline = [
  //demoInteractiveBoard, 
  instructions, comprehension_check];

var familiarization_loop = {
  timeline: familiarization_timeline,
  loop_function: function (data) {
    return !familiarization_check_correct;
  },
};

if (official_run) {
  timeline.push(familiarization_loop);
}

var final_instructions = {
  type: "instructions",
  pages: [
    "<p> Now you are ready to begin! </p>" +
    '<p> Please click <strong>"Next"</strong> to start the experiment.</p>' +
    "<p> Thank you for participating in our study! </p>",
  ],
  show_clickable_nav: true,
};
timeline.push(final_instructions);

const updateClicksRemaining = (event) => {
  const clicksRemainingDisplay = document.getElementById('clicksRemaining');
  const remaining = maxClicks - totalClicks();
  clicksRemainingDisplay.textContent = remaining;
};

let boundHandleClick = null;

function createClickHandler(selectedColor) {
  return function handleClick(event) {
    const cell = event.target;
    const cellId = cell.id;

    // Ignore clicks on input fields or text areas
    if (cell.tagName === 'INPUT' || cell.tagName === 'TEXTAREA') {
      return;
    }

    if (
      cell.classList.contains('cell') &&
      (cell.style.backgroundColor == "" || 
       cell.style.backgroundColor == "white" || 
       !noModifyCells.has(cellId)) &&
      selectedColor
    ) {
      if (totalClicks() >= maxClicks) {
        alert("You've reached the maximum number of clicks!\nPlease CLEAR if you would like to revise your selections.");
        return;
      }

      clickCounts[cellId] = (clickCounts[cellId] || 0) + 1;
      const intensity = Math.min(clickCounts[cellId], 10) / 10;
      const [r, g, b] = selectedColor === "blue" ? [0, 0, 255] : [255, 0, 0];
      
      cell.style.backgroundColor = `rgb(${
        Math.round(255 - (255 - r) * intensity)}, ${
        Math.round(255 * (1 - intensity))}, ${
        Math.round(255 - (255 - b) * intensity)})`;

      const clickCountSpan = document.createElement('span');
      clickCountSpan.textContent = clickCounts[cellId];
      clickCountSpan.style.fontFamily = 'Consolas, "Courier New", monospace';
      clickCountSpan.style.fontSize = '0.8em';
      clickCountSpan.style.position = 'absolute';
      clickCountSpan.style.top = '2px';
      clickCountSpan.style.right = '2px';
      clickCountSpan.style.color = 'grey';
      
      // Clear existing content and add the styled span
      cell.textContent = '';
      cell.style.position = 'relative';
      cell.appendChild(clickCountSpan);
        

      console.log("CLICKED!!!! clicked cell id: ", cellId)
      
      
      modifiedCells.add(cellId);
      last_cell = cell;

      updateClicksRemaining();

      // if (totalClicks() >= minClicks) {
      if ((totalClicks() >= minClicks) && (timerElapsed)) {
        const btn = document.getElementById('jspsych-survey-html-form-next');
        btn.disabled = false;
        btn.style.background = "#112242";
      }

      updateHoverEffect(null);
      document.querySelectorAll('.cell').forEach(cell => {
        cell.classList.remove('hover-grey');
        cell.classList.add('hover-grey');
      });
    }
  };
}


var timerElapsed = false;
var timeRemaining = suggestionForcedRespTime;
var predictBoard = {
  type: "survey-html-form",
  //trial_duration: min_seconds * 1000, // in msec
  html: function () {
    var task = jsPsych.timelineVariable("task");
    var board_rows = jsPsych.timelineVariable("board_rows");
    var board_cols = jsPsych.timelineVariable("board_cols");
    var win_conditions = jsPsych.timelineVariable("win_conditions");

    var predPlayerAtIdxs = jsPsych.timelineVariable('player_at_idx')
    var predPlayer = predPlayerAtIdxs[gameStage]

    if (predPlayer == 1){
      selectedColor = 'blue'
      updateHoverEffect('hover-blue');
    } else{
      selectedColor = 'red'
      updateHoverEffect('hover-red');
    }

    var opener_txt = `<p>Two players are playing on a <strong>${board_rows} x ${board_cols} board</strong>.</p>`;

    var task_txt = "<p>The rules for this game are that: <strong>" + win_conditions + "</strong></p>";

    var task_msg = "<p><strong>What do you think the <span style='color:" + selectedColor + ";'>" + selectedColor.toUpperCase() + "</span> player <strong>should</strong> do next?</strong> Indicate where you think the player SHOULD move by clicking on the board.</p>" + 
     "<p style='display: inline-block; width: 80%;'>The more times you click in a cell, the more confident you are the player should move there. When you are happy with your selections, press SUBMIT. You must spend at least " + suggestionForcedRespTime + " seconds before submitting.</p>" +
    `<div id="clickCounter" style="
      display: inline-block;
      vertical-align: top;
      background-color: #f5f5f5;
      padding: 8px;
      border-radius: 6px;
      box-shadow: 0 1px 3px rgba(0,0,0,0.1);
      width: 100px;
      text-align: center;
      font-size: 14px;
      margin-left: 20px;
    ">
      <div style="margin-bottom: 4px;">Clicks Remaining</div>
      <div id="clicksRemaining" style="
        font-size: 20px;
        font-weight: bold;
        color: #000;
        margin-bottom: 4px;
      ">${maxClicks}</div>
    </div>`;

    var viz_html = `
      <p></p><br></br>
      <div style="width: 100%; text-align: center;">
        <div id="gameBoard"></div>
        <div style="margin-top: 20px;">
          <input type="button" id="clear-btn" type="buttons" class="buttons" value="CLEAR CLICKS"></input>
        </div>
      </div>`;

    return opener_txt + task_txt + task_msg + viz_html;
  },
  button_label: "SUBMIT", //"CONTINUE TO QUESTION",

  on_load: function () {
    // reset 
    clickCounts = {}

    selectedColor = "grey"

    const gameBoard = document.getElementById('gameBoard');
    // let selectedColor = 'white';
    const clearBtn = document.getElementById("clear-btn");
    // const undoBtn = document.getElementById("undo-btn");

    const clicksRemainingDisplay = document.getElementById('clicksRemaining');

    const btn = document.getElementById('jspsych-survey-html-form-next')
    // btn.classList.add("buttons")
    btn.disabled = true
    btn.style.background = "#A8A8A8";

    // timeRemaining = suggestionForcedRespTime;
    


    if (official_run) {
      var time_delay = min_seconds * 1000
    } else {
      var time_delay = 5000
    }

    var rows = jsPsych.timelineVariable("board_rows");
    var cols = jsPsych.timelineVariable("board_cols");

    // var rows = "3"
    // var cols = "4"

    const maxWidth = window.innerWidth * 0.4;
    const maxHeight = window.innerHeight * 0.4;

    // Set the width of each cell to maintain square shape
    const cellSize = Math.min(maxWidth / cols, maxHeight / rows);


    var predMoveIdxs = jsPsych.timelineVariable('pred_move_idxs')

    var predMove = predMoveIdxs[gameStage] - 1 

    var currentBoard = boardStates[predMove]
    for (let row = 0; row < rows; row++) {
      for (let col = 0; col < cols; col++) {
        const cell = document.createElement('div');
        cell.id = `${row}-${col}`;


        cell.classList.add('cell');
        cell.style.width = `${cellSize}px`;
        cell.style.height = `${cellSize}px`;

        // Assign color based on currentBoard value
        if (row < currentBoard.length && col < currentBoard[row].length) {

          if (currentBoard[row][col] === 1) {
            cell.style.backgroundColor = BASE_BLUE; // First player
            noModifyCells.add(cell.id);
          } else if (currentBoard[row][col] === 2) {
            cell.style.backgroundColor = BASE_RED; // Second player
            noModifyCells.add(cell.id);
          } else {
            cell.style.backgroundColor = "white"; // Blank
          }
        } else {
          cell.style.backgroundColor = "white"; // Default to blank

        }

        currentMaxMoveShown = predMove
        const moveNumber = getMoveNumber(moveHistory, row, col, currentMaxMoveShown);
        if (moveNumber) {
          cell.textContent = moveNumber;
          cell.style.color = "black";
        }

        // Add click event to track modifications
        cell.addEventListener('click', () => {
          modifiedCells.add(cell.id);
        });

        // if (totalClicks() === maxClicks) {
        //   btn.disabled = false;
        //   btn.style.background = "#112242";
        // }

        gameBoard.appendChild(cell);
      }
    }
    // Update the grid template based on the number of columns
    gameBoard.style.gridTemplateColumns = `repeat(${cols}, ${cellSize}px)`;

    document.querySelectorAll('.cell').forEach(cell => {
      cell.classList.remove('hover-grey');
      cell.classList.add('hover-grey');

    });

        // Start timer

      
    var timer = setInterval(() => {
      timeRemaining--;
      // if (timeRemainingDisplay) {
      //   timeRemainingDisplay.textContent = `Time remaining: ${Math.max(0, timeRemaining)}s`;
      // }
      
      console.log("time remaining: ", timeRemaining)

      if (timeRemaining <= 0) {
        clearInterval(timer);
        timerElapsed = true;
        // if (timeRemainingDisplay) {
        //   timeRemainingDisplay.textContent = 'Timer complete';
        //   timeRemainingDisplay.style.color = 'green';
        // }
        // checkButtonStatus();
        if ((totalClicks() >= minClicks) && (timerElapsed)) {
          console.log("submitting from here")
          const btn = document.getElementById('jspsych-survey-html-form-next');
          btn.disabled = false;
          btn.style.background = "#112242";
        }
      }
    }, 1000);

    

    var predPlayerAtIdxs = jsPsych.timelineVariable('player_at_idx')
    console.log('on game stage: ', gameStage, predPlayerAtIdxs)
    var predPlayer = predPlayerAtIdxs[gameStage]

    console.log('pred player: ', predPlayer)

    if (predPlayer == 1){
      selectedColor = 'blue'
      updateHoverEffect('hover-blue');
    } else{
      selectedColor = 'red'
      updateHoverEffect('hover-red');
    }


    boundHandleClick = createClickHandler(selectedColor);
    document.addEventListener('click', boundHandleClick);

    // Clear functionality
    clearBtn.addEventListener("click", () => {
      document.querySelectorAll('.cell').forEach(cell => {
        const [row, col] = cell.id.split('-').map(Number);

        // Revert only modified cells
        if (modifiedCells.has(cell.id)) {
          if (row < currentBoard.length && col < currentBoard[row].length) {
            if (currentBoard[row][col] === 1) {
              cell.style.backgroundColor = BASE_BLUE; // Revert to original color
            } else if (currentBoard[row][col] === 2) {
              cell.style.backgroundColor = BASE_RED; // Revert to original color
            } else {
              cell.style.backgroundColor = "white"; // Reset to blank
            }
          } else {
            cell.style.backgroundColor = "white"; // Default to blank
          }

          // Reset text content
          cell.textContent = "";
        }
      });

      // Reset state
      modifiedCells.clear();
      
      
      last_cell = "";
      // single_sim_board_state.push(["CLEAR", "CLEAR"]);
      all_click_traces.push(clickCounts);
      clickCounts = {}
      num_clear_clicks+=1
      updateClicksRemaining();
      console.log("click counts: ", clickCounts)
      // single_sim_board_state = [];
      //selectedColor = "grey";
      // disable again
      btn.disabled = true
      btn.style.background = "#A8A8A8";

      // Update hover effect
      document.querySelectorAll('.cell').forEach(cell => {
        cell.classList.remove('hover-grey');
        cell.classList.add('hover-grey');
      });

      console.log("Board cleared! Click counts reset.");
    });

  },
  on_finish: function () {
    // help from: https://www.jspsych.org/7.0/reference/jspsych-data/index.html

    // add final set of accumulated moves (b/c only stored with reset)
    all_click_traces.push(clickCounts)

    console.log("num clear clicks: ", num_clear_clicks);
    console.log("board states: ", all_click_traces);

    var board_cols = jsPsych.timelineVariable("board_cols")
    var board_rows = jsPsych.timelineVariable("board_rows")
    var stim_tag = jsPsych.timelineVariable("stim_tag")
    var win_conditions = jsPsych.timelineVariable("win_conditions")

    var data = { "num_clear": num_clear_clicks, 
      "click_counts": clickCounts, 
      "all_click_traces": all_click_traces, 
      "stim_tag": stim_tag, "board_cols": board_cols, "board_rows": board_rows, 
      "win_conditions": win_conditions, "page_type": "scratchpad" };

    // reset timer
    timerElapsed = false; 
    timeRemaining = suggestionForcedRespTime; 
    
    jsPsych.data.get().push(data);
    num_clear_clicks = 0;
    currentPlayer = "";
    all_click_traces = [];
    modifiedCells = new Set();
    // noModifyCells = new Set();
    // boardStates = []
    // clickCounts = {}
    clickCounts = {}
    if (boundHandleClick) {
      document.removeEventListener('click', boundHandleClick);
      boundHandleClick = null;
    }
    console.log("removed listener")
    gameStage+=1

  },
};

var ratingPage = {
  type: "multiple-slider",
  preamble: function () {
    var board_rows = jsPsych.timelineVariable("board_rows");
    var board_cols = jsPsych.timelineVariable("board_cols");
    var task = jsPsych.timelineVariable("task");

    var opener_txt = `<p>Games take place on a <strong>${board_rows} x ${board_cols} board</strong>.</p>`;

    var task_txt = "<p>The rules for this game are that: <strong>" +
      jsPsych.timelineVariable("win_conditions") +
      "</strong></p>";

      var board_comment = `<p>This particular match, between these particular players, ended in the following configuration: <br><br>`
      var board_obj = `
      <div id="container" style="text-align: center;">
        <div id="finalGameBoard" style="display: grid; justify-content: center; margin: 20px auto;"></div>
      </div><br><br>`

    var prompt_txt = opener_txt + board_comment + board_obj + task_txt;

    return prompt_txt + 
      `<p>    </p>`;
  },
  questions: function () {
    var slider_questions = []

    // slider_questions.push(turing_test_slider)

    slider_questions.push(...skill_sliders)

    // slider_questions.push(
    //   {
    //     prompt: "<p><strong>How likely do you think this game was played by two computers or two humans?</strong></p><p>    </p>",
    //     name: "response",
    //     labels: ['Certainly computers', 'No clue', 'Certainly humans'],
    //     required: true,
    //   },
    // )
    if (task.includes("fun")) {
      slider_questions.push(
        {
          prompt: "<p><strong>" + task_questions[task]["q_fmt"] + "</strong></p><p>    </p>",
          name: "response",
          labels: scales[jsPsych.timelineVariable("task")],
          required: true,
        },
      )
    } else {
      slider_questions.push(...advantage_sliders)
    }
    return slider_questions
  },
  randomize_question_order: false,
  on_load: function() {
    // Get final board state
    const finalBoardState = boardStates[boardStates.length - 1];
    const rows = finalBoardState.length;
    const cols = finalBoardState[0].length;

    // Calculate cell size
    const maxWidth = window.innerWidth * 0.4;
    const maxHeight = window.innerHeight * 0.4;
    const cellSize = Math.min(maxWidth / cols, maxHeight / rows);

    const boardContainer = document.getElementById('finalGameBoard');
    boardContainer.style.gridTemplateColumns = `repeat(${cols}, ${cellSize}px)`;
    boardContainer.style.gridGap = "2px";

    // Create the board
    for (let row = 0; row < rows; row++) {
      for (let col = 0; col < cols; col++) {
        const cell = document.createElement('div');
        cell.style.width = `${cellSize}px`;
        cell.style.height = `${cellSize}px`;
        cell.style.border = "1px solid black";
        cell.style.display = "flex";
        cell.style.justifyContent = "center";
        cell.style.alignItems = "center";

        // Set cell color based on board state
        if (finalBoardState[row][col] === 1) {
          cell.style.backgroundColor = BASE_BLUE;
          cell.style.color = "black";
        } else if (finalBoardState[row][col] === 2) {
          cell.style.backgroundColor = BASE_RED;
          cell.style.color = "black";
        } else {
          cell.style.backgroundColor = "white";
        }

        // Add move number if this cell was played
        const moveNumber = getMoveNumber(moveHistory, row, col, boardStates.length - 1);
        if (moveNumber) {
          cell.textContent = moveNumber;
          cell.style.color = "black";
        }

        boardContainer.appendChild(cell);
      }
    }
  }
};
var rating_task = {
  timeline: [readStimuli, watchBoard, predictBoard, watchBoard, predictBoard, watchBoard, predictBoard, ratingPage],
  timeline_variables: stimuli_batch,
  data: {
    task: jsPsych.timelineVariable("task"),
    board_cols: jsPsych.timelineVariable("board_cols"),
    board_rows: jsPsych.timelineVariable("board_rows"),
    stim_tag: jsPsych.timelineVariable("stim_tag"),
    win_conditions: jsPsych.timelineVariable("win_conditions"),
    arena: jsPsych.timelineVariable('arena'),
    game_tag: jsPsych.timelineVariable('game_tag'), 
    pred_move_idxs: jsPsych.timelineVariable('pred_move_idxs'),
    source: jsPsych.timelineVariable('source'),
    metatask: "full_info_gameplay_scratchpad_autoswitch",
  },
  sample: {
    type: "custom",
    fn: function (t) {
      // t = set of indices from 0 to n-1, where n = # of trials in stimuli variable
      // returns a set of indices for trials

      // randomize order of goals + plans to show
      return jsPsych.randomization.shuffle(t);
    },
  },
  on_finish: function () {
    var curr_progress_bar_value = jsPsych.getProgressBarCompleted();
    moveHistory = [];
    modifiedCells = new Set();
    noModifyCells = new Set();
    boardStates = []
    clickCounts = {}
    jsPsych.setProgressBar(curr_progress_bar_value + progress_bar_increase);
  },
};

timeline.push(rating_task);


var freq_scale = ["No prior experience",
  "Some prior experience playing",
  "Substantial prior experience playing"]


var experience_page = {
  type: "multiple-slider",
  preamble: function () {
    var prompt_txt = `<p>Thank you for participating in our study! Before finishing, <strong>read the following questions carefully and give your answer on the scales.</strong></p><p>We will then ask a brief series of open text questions, and then you are done! We will give a completion code after the brief next two questionarres. Thank you for your time!`;
    return prompt_txt
  },
  questions: [
    {
      prompt: `<p>How much <strong>time did you spend thinking</strong> about your prediction of what they should do, on average?</p>`,
      name: "thinking-time",
      labels: ["< 30 seconds", "1-2 minutes", "> 2 minutes"], //["30 seconds or less", "Around 1 minute", "2 or more minutes"],
      required: true,
    },
    {
      prompt: `<p>How much <strong>fun</strong> was this experiment?</p>`,
      name: "exp-fun",
      labels: ["The most boring experiment imaginable", "Neutral", "The most fun experiment imaginable"],
      required: true,
    },
    {
      prompt: `<p>How <strong>challenging</strong> was this experiment?</p>`,
      name: "exp-challenge",
      labels: ["The least challenging experiment imaginable", "Neutral", "The most challenging experiment imaginable"],
      required: true,
    },
    {
      prompt: `<p>How did you find the video play-speed?</p>`,
      name: "play speed",
      labels: ["Way too slow", "Just right", "Way too fast"],
      required: true,
    },
    {
      prompt: `<p>How much prior experience do you have with the game:<p></p><strong>Tic-Tac-Toe</strong>?</p>`,
      name: "tic-tac-toe",
      labels: freq_scale,
      required: true,
    },
    {
      prompt: `<p>How much prior experience do you have with the game:<p></p><strong>Connect 4</strong>?</p>`,
      name: "connect-4",
      labels: freq_scale,
      required: true,
    },
    {
      prompt: `<p>How much prior experience do you have with the game:<p></p><strong>Gomoku</strong> (5-in-a-row)?</p>`,
      name: "gomoku",
      labels: freq_scale,
      required: true,
    },
  ],
  randomize_question_order: false,
};

// timeline.push(experience_page)

var questions = [];

questions.push({
  prompt:
    "How much fun did you find the experiment?",
  rows: 5,
  columns: 50,
  required: true,
});

questions.push({
  prompt:
    "How challenging did you find the experiment?",
  rows: 5,
  columns: 50,
  required: true,
});

questions.push({
  prompt:
    "How much time did you think you spent on each prediction question? (estimate in seconds)",
  rows: 5,
  columns: 50,
  required: true,
});

questions.push({
  prompt:
    "How did you come up with answers for the questions? Please explain the strategies you used to think about each game?",
  rows: 5,
  columns: 50,
  required: true,
});

questions.push({
  prompt:
    "Were the questions easier to answer for some games than for others? If so, why?",
  rows: 5,
  columns: 50,
  required: true,
});

// questions.push({
//   prompt:
//     "Was it hard to tell whether videos were two computers or two humans? What features did you pay attention to?",
//   rows: 5,
//   columns: 50,
//   required: true,
// });

questions.push({
  prompt:
    "How did you find the speed of the video? Too slow? Just right? Too fast?",
  rows: 5,
  columns: 50,
  required: true,
});

questions.push({
  prompt: "Do you have any additional comments to share with us?",
  rows: 5,
  columns: 50,
});

var comments_block = {
  type: "survey-text",
  preamble:
    "<p>Thank you for participating in our study!</p>" +
    '<p>Click <strong>"Finish"</strong> to complete the experiment and receive compensation. If you have any comments about the experiment, please let us know in the form below.</p>',
  questions: questions,
  button_label: "Finish",
  on_load: function() {
    // First, remove all game-related event listeners
    if (boundHandleClick) {
      document.removeEventListener('click', boundHandleClick);
      boundHandleClick = null;
    }
    
    // Remove any keydown listeners
    const oldListener = document.onkeydown;
    document.onkeydown = null;
    
    // Clean up any jsPsych keyboard listeners
    if (typeof jsPsych !== 'undefined') {
      if (jsPsych.pluginAPI && jsPsych.pluginAPI.cancelAllKeyboardResponses) {
        jsPsych.pluginAPI.cancelAllKeyboardResponses();
      }
    }
    
    // Enable and fix all textareas
    document.querySelectorAll('textarea').forEach(textarea => {
      // Remove any existing event listeners
      const newTextarea = textarea.cloneNode(true);
      textarea.parentNode.replaceChild(newTextarea, textarea);
      
      // Ensure the textarea is enabled and focusable
      newTextarea.disabled = false;
      newTextarea.readOnly = false;
      newTextarea.style.pointerEvents = 'auto';
      
      // Add a click handler to ensure focus works
      newTextarea.addEventListener('click', function(e) {
        e.stopPropagation();
        this.focus();
      });
    });

    // Add CSS to ensure textareas are interactive
    const style = document.createElement('style');
    style.innerHTML = `
      textarea {
        pointer-events: auto !important;
        background: white !important;
        color: black !important;
        cursor: text !important;
      }
      textarea:focus {
        outline: 2px solid #4A90E2 !important;
      }
    `;
    document.head.appendChild(style);
  }
};
timeline.push(comments_block);


var finalPage = {
  type: "instructions",
  pages: ["<p>Thank you for participating in our study!</p>" +
    '<p>Click <strong>"Finish"</strong> to complete the experiment and receive compensation. If you have any comments about the experiment, please let us know on Prolific chat.</p>'],
  show_clickable_nav: true,
};
timeline.push(finalPage);

/* finish connection with pavlovia.org */
var pavlovia_finish = {
  type: "pavlovia",
  command: "finish",
};
timeline.push(pavlovia_finish);

// todo: update w/ proper prolific link!!
jsPsych.init({
  timeline: timeline,
  on_finish: function () {
    // send back to main prolific link
    // window.location = "https://www.google.com/"
    window.location =
      "https://app.prolific.co/submissions/complete?cc=CAJ3UU4G";
  },
  show_progress_bar: true,
  auto_update_progress_bar: false,
});
