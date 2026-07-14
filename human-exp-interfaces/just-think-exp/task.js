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

var task_questions = {
  how_fun: {
    q_fmt: "How fun is this game?",
    instruct_fmt: "how fun the game is to play",
  },
  advantage: {
    q_fmt: "Assuming both players play reasonably -- if the game does not end in a draw, how likely is it that the first player is going to win (not draw), and how likely is a draw?",
    instruct_fmt:
      "assuming both players play reasonably -- if the game does not end in a draw, how likely is it that the first player is going to win (not draw), and how likely is a draw",
  },
};

var advantage_sliders = [
  { 
    prompt: "<p><strong>" + "If the game <i>does not end in a draw</i>, assuming both players play reasonably, how likely is it that the first player is going to win (<i>not draw</i>)?" + "</strong></p><p>    </p>",
    name: "firstplayer_response",
    labels: [
          "First player definitely going to <strong>lose</strong>",
          "Equally likely to <strong>win or lose</strong>",
          "First player definitely going to <strong>win</strong>",
        ],
    required: true,
  },
  {
    prompt: "<p><strong>" + "Assuming both players play reasonably, how likely is the game to end in a draw?" + "</strong></p><p>    </p>",
    name: "draw_response",
    labels: ["Impossible to end in a draw", "Equally likely to end in a draw or not",
      "Definitely going to end in a draw",],
    required: true,
  },

];

// pick a random condition for the subject at the start of the experiment
// help from: https://www.jspsych.org/overview/prolific/
// based on our total number of batches <--- note: can subset if we need to run some a few more
var num_batches = 24;
var conditions = Array.from(Array(num_batches).keys()); // help from: https://www.codegrepper.com/code-examples/javascript/javascript+create+list+of+numbers+1+to+n

var rem_conds = []
var conditions = conditions.filter((n) => !rem_conds.includes(n));
console.log("conditions: ", conditions);


var condition_num = jsPsych.randomization.sampleWithoutReplacement(
  conditions,
  1
)[0];


var min_seconds = 60 // minimum amt of time to spend (in seconds)

console.log("condition num: ", condition_num)

var official_run = true;

// record the condition assignment
jsPsych.data.addProperties({
  condition: condition_num,
});

var stimuli_batch = batch_data[condition_num];
console.log(" batch: ", condition_num);
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
var base_rate = 12.5;
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


var num_clicks = 0;
var all_board_states = [];
var single_sim_board_state = [];
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

function handleClick(event){
  if ((event.target.classList.contains('cell')) && (event.target.style.backgroundColor == "" || event.target.style.backgroundColor == "white") && (selectedColor != "")) {
    console.log("BKGRD: ", event.target.style.backgroundColor)
    event.target.style.backgroundColor = selectedColor;
    console.log("Selected!!", event.target, event.target.id, selectedColor)
    var cell_id_clicked = event.target.id
    // if (selectedColor != "white" && selectedColor != "") {
    //   console.log("Clicked!! ", cell_id_clicked)
    //   single_sim_board_state.push([cell_id_clicked, selectedColor])
    // };
    single_sim_board_state.push([cell_id_clicked, selectedColor])
    last_cell = event.target
    // selectedColor = ""
    updateHoverEffect(null); // Remove hover effect after click


    if (selectedColor === "red"){
      selectedColor = "blue"
      //updateHoverEffect('hover-blue');
      document.querySelectorAll('.cell').forEach(cell => {
        cell.classList.remove('hover-blue', 'hover-red', 'hover-green');
          if (event) {
              cell.classList.add('hover-blue');
          }
      });
    } else if (selectedColor === "blue"){
      selectedColor = "red"
      document.querySelectorAll('.cell').forEach(cell => {
        cell.classList.remove('hover-blue', 'hover-red', 'hover-green');
          if (event) {
              cell.classList.add('hover-red');
          }
      });
    }

}
}

function handleKeyDown(event){
  console.log("KEY!! ", event.key)
    if (event.key === 'Space' || event.key === ' ') {
      console.log("going to switch!! ", selectedColor)
      if (selectedColor === "red"){
        selectedColor = "blue"
        updateHoverEffect('hover-blue');
      } else if (selectedColor === "blue"){
        selectedColor = "red"
        updateHoverEffect('hover-red');
      }
    }
}


var demoInteractiveBoard  = {
  type: "survey-html-form",
  html: function() { 
    console.log("STIMULI!!")
    return construct_demo_scratchpad_stimuli()

  }, 
  button_label: "NEXT",

  on_load: function() {

    console.log("LOADED!!")

    selectedColor = "blue"
    
    // document.addEventListener('DOMContentLoaded', () => {
      const gameBoard = document.getElementById('gameBoard');
      const clearBtn = document.getElementById("clear-btn");
      const undoBtn = document.getElementById("undo-btn");

      const btn = document.getElementById('jspsych-survey-html-form-next')
      // btn.classList.add("buttons")
      btn.style.background = "#112242";

      var rows = 5;
      var cols = 5; 

      const maxWidth = window.innerWidth * 0.4;
      const maxHeight = window.innerHeight * 0.4;

      // Set the width of each cell to maintain square shape
      const cellSize = Math.min(maxWidth / cols, maxHeight / rows);

      // Initialize the board
      for (let i = 0; i < rows * cols; i++) {
          const cell = document.createElement('div');
          cell.classList.add('cell');
          cell.style.width = `${cellSize}px`;
          cell.style.height = `${cellSize}px`;
          gameBoard.appendChild(cell);
      }

      // Update the grid template based on the number of columns
      gameBoard.style.gridTemplateColumns = `repeat(${cols}, ${cellSize}px)`;

      document.querySelectorAll('.cell').forEach(cell => {
        cell.classList.remove('hover-blue', 'hover-red', 'hover-green');
          cell.classList.add('hover-blue');
        
      });

// Event listener for coloring cells and removing hover effect
document.addEventListener('click', handleClick);

// Event listener for key presses
document.addEventListener('keydown', handleKeyDown);




undoBtn.addEventListener("click", () => {
  console.log("UNDO! last: ", last_cell)
  if (last_cell != ""){
    console.log("reset: ", last_cell)
    last_cell.style.backgroundColor =''; //'white';
    last_cell = ""
    if (selectedColor === "red"){
      selectedColor = "blue"
      //updateHoverEffect('hover-blue');
      document.querySelectorAll('.cell').forEach(cell => {
        cell.classList.remove('hover-blue', 'hover-red', 'hover-green');
         cell.classList.add('hover-blue');
      });
    } else if (selectedColor === "blue"){
      selectedColor = "red"
      document.querySelectorAll('.cell').forEach(cell => {
        cell.classList.remove('hover-blue', 'hover-red', 'hover-green');
        cell.classList.add('hover-red');

      });
    }
  }
});

      clearBtn.addEventListener("click", () => {
        document.querySelectorAll('.cell').forEach(cell => {
          cell.style.backgroundColor = '';
        });
        // boardState = Array.from({ length: numRows * numCols }, () => "");
        // currentPlayer = "";
        num_clicks += 1;
        last_cell = ""

        selectedColor = "blue"
      //updateHoverEffect('hover-blue');
      document.querySelectorAll('.cell').forEach(cell => {
        cell.classList.remove('hover-blue', 'hover-red', 'hover-green');
         cell.classList.add('hover-blue');

         

      });
    });
  

  }, 
  on_finish: function () {


    document.addEventListener('click', handleClick)
    document.addEventListener('keydown', handleKeyDown)
  } 
}









var interactiveBoard = {
  type: "survey-html-form",
  //trial_duration: min_seconds * 1000, // in msec
  html: function () {
    var task = jsPsych.timelineVariable("task");
    var board_rows = jsPsych.timelineVariable("board_rows");
    var board_cols = jsPsych.timelineVariable("board_cols");
    var win_conditions = jsPsych.timelineVariable("win_conditions");

    var opener_txt = `<p><strong>In this game,</strong> imagine you are playing on a <strong>${board_rows} x ${board_cols} board</strong>.</p>`;

    var task_txt =
      "<p>The rules for this game are that: <strong>" +
      win_conditions+
      "</strong></p>";

    // Add a message to prompt the user to select a player
    // var player_select_msg = "<p>You are <strong>free to use the scratchpad below</strong>, but are <i>not required</i>. To use it: type a key (A-Z) to select a player marker and click on a grid cell to place the piece. You can clear the board by pressing <strong>CLEAR</strong>.";
    var player_select_msg = "<p>You are <strong>free to use the scratchpad below</strong>, but are <i>not required</i>. To use it: click on a cell to place a piece. Pieces are colored either <span style='color: blue'>blue</span> or <span style='color: red'>red</span>. As you place pieces, the colors will automatically alternate. If you instead want to play the same color again, press the <strong>SPACE</strong> bar before placing the piece.</p><p>You can undo your last move by pressing <strong>UNDO</strong> or clear the board entire by pressing <strong>CLEAR</strong>.</p>"; 

    var submit_msg = "<p>When you feel you understand the game and are ready to respond, press the <strong>CONTINUE TO QUESTION button</strong>. You must spend <strong>at least 60 seconds</strong> before you are able to proceed.</p>"
    

    var prompt_txt = opener_txt + task_txt + player_select_msg + submit_msg; // + "<p><strong>" + task_questions[task] + "</strong></p>"
    var viz_html =
      `<p></p><br></br>
        <center><div id="gameBoard"></div></center>
        <input type="button" id="undo-btn" type="buttons" class="buttons" value="UNDO"></input><input type="button" id="clear-btn" type="buttons" class="buttons" value="CLEAR"></input></p>`; 
    //         <p>` +
    // //   task_questions[task]["q_fmt"] + 
    //   `</p>`;
    return prompt_txt + viz_html;
  },
  //choices: [" ", "Spacebar"],
  button_label: "CONTINUE TO QUESTION",

  on_load: function() {

    single_sim_board_state = []

    selectedColor = "blue"
    //updateHoverEffect('hover-blue')
    
    
    // document.addEventListener('DOMContentLoaded', () => {
      const gameBoard = document.getElementById('gameBoard');
      // let selectedColor = 'white';
      const clearBtn = document.getElementById("clear-btn");
      const undoBtn = document.getElementById("undo-btn");

      const btn = document.getElementById('jspsych-survey-html-form-next')
      // btn.classList.add("buttons")
      btn.disabled=true
      btn.style.background = "#A8A8A8";
	

		if (official_run){
			var time_delay = min_seconds * 1000
		}else{
			var time_delay = 5000
		}
    //var time_delay = 10000

		setTimeout(function(){
			btn.disabled = false;
			console.log('Button Activated')
			btn.style.background = "#112242";
      // document.querySelector('jspsych-survey-html-form-next').src = 'imgB.png'
    }, time_delay);

      var rows = jsPsych.timelineVariable("board_rows");
      var cols = jsPsych.timelineVariable("board_cols"); 

      //rows = "Infinity"

      var is_inf = false 
      
      // for now, both cols + row are both inf
      if (rows == "Infinity"){

        rows = 13
        cols = 13

        is_inf = true

      }else{
        rows = parseInt(rows)
        cols = parseInt(cols)
      }

      const maxWidth = window.innerWidth * 0.4;
      const maxHeight = window.innerHeight * 0.4;

      // Set the width of each cell to maintain square shape
      const cellSize = Math.min(maxWidth / cols, maxHeight / rows);
      

      // Initialize the board
      for (let i = 0; i < rows * cols; i++) {
          const cell = document.createElement('div');
          cell.id = i
          //cell.style.backgroundColor = "white"
          cell.classList.add('cell');
          cell.style.width = `${cellSize}px`;
          cell.style.height = `${cellSize}px`;

          if (is_inf){
            if (i < rows) { 
              // Set each border side individually
              cell.style.borderTop = "dashed";           // Remove top border
            }
            if (i % rows == 0){ 
              cell.style.borderLeft=  "dashed"; // none
            }
            if (i % rows == cols - 1){ 
              cell.style.borderRight=  "dashed"; 
            }
            if (i >= rows * (cols - 1)){
              cell.style.borderBottom = "dashed";
            }
            
          }


          gameBoard.appendChild(cell);
      }

      // Update the grid template based on the number of columns
      gameBoard.style.gridTemplateColumns = `repeat(${cols}, ${cellSize}px)`;

      document.querySelectorAll('.cell').forEach(cell => {
        cell.classList.remove('hover-blue', 'hover-red', 'hover-green');
          cell.classList.add('hover-blue');
        
      });



document.addEventListener('click', handleClick)
document.addEventListener('keydown', handleKeyDown)


undoBtn.addEventListener("click", () => {
  console.log("UNDO! last: ", last_cell)
  if (last_cell != ""){
    console.log("reset: ", last_cell)
    last_cell.style.backgroundColor =''; //'white';
    last_cell = ""
    single_sim_board_state.push(["UNDO", "UNDO"])
    if (selectedColor === "red"){
      selectedColor = "blue"
      //updateHoverEffect('hover-blue');
      document.querySelectorAll('.cell').forEach(cell => {
        cell.classList.remove('hover-blue', 'hover-red', 'hover-green');
         cell.classList.add('hover-blue');
      });
    } else if (selectedColor === "blue"){
      selectedColor = "red"
      document.querySelectorAll('.cell').forEach(cell => {
        cell.classList.remove('hover-blue', 'hover-red', 'hover-green');
        cell.classList.add('hover-red');

      });
    }
  }
});

      clearBtn.addEventListener("click", () => {
        document.querySelectorAll('.cell').forEach(cell => {
          cell.style.backgroundColor = '';
        });
        // boardState = Array.from({ length: numRows * numCols }, () => "");
        // currentPlayer = "";
        num_clicks += 1;
        last_cell = ""
        single_sim_board_state.push(["CLEAR", "CLEAR"])
        all_board_states.push(single_sim_board_state);
        single_sim_board_state = [];
        selectedColor = "blue"
      //updateHoverEffect('hover-blue');
      document.querySelectorAll('.cell').forEach(cell => {
        cell.classList.remove('hover-blue', 'hover-red', 'hover-green');
         cell.classList.add('hover-blue');

         

      });
    });
  // });
  

  },
  on_finish: function () {
    // help from: https://www.jspsych.org/7.0/reference/jspsych-data/index.html

    // add final set of accumulated moves (b/c only stored with reset)
    all_board_states.push(single_sim_board_state)

    console.log("num clear clicks: ", num_clicks);
    console.log("board states: ", all_board_states);

    var board_cols = jsPsych.timelineVariable("board_cols")
    var board_rows = jsPsych.timelineVariable("board_rows")
    var stim_tag= jsPsych.timelineVariable("stim_tag")
    var win_conditions = jsPsych.timelineVariable("win_conditions")

    var data = { "num_clear": num_clicks, "board_states": all_board_states, "stim_tag":  stim_tag, "board_cols": board_cols, "board_rows": board_rows, "win_conditions": win_conditions, "page_type": "scratchpad"};
    num_clicks = 0;
    currentPlayer = ""; 
    all_board_states = [];
    jsPsych.data.get().push(data);

    document.removeEventListener("click", handleClick);
    document.removeEventListener("keydown", handleKeyDown);

  },
};

var construct_demo_scratchpad_stimuli = function(){
    var board_rows = "5";
    var board_cols = "5";
    var win_conditions = "3 in a row wins."; 

    var opener_txt = `<p>Here is an example scratchpad for a <strong>${board_rows} x ${board_cols} board</strong>. You mark the scratchpad by coloring in cells on the grid.</p>` + 
    `<p>To use the scratchpad, click on a cell to place a piece. You can first hover over a cell. <strong>Then, to confirm a move, click on a grid cell</strong> to color the piece.</p><p><i>Different players are marked by colors.</strong></i> Pieces are colored either <span style='color: blue'>blue</span> or <span style='color: red'>red</span>. As you place pieces, the colors will automatically alternate. If you instead want to play the same color again, press the <strong>SPACE</strong> bar before placing the piece.</p>` + 
    '<p>You can undo your last move by pressing <strong>UNDO</strong> or clear the board entire by pressing <strong>CLEAR</strong>.</p>' +
    '<p>As a reminder, <strong>use of the scratchpad is optional. You are free to use it however you like.</strong> Press the <strong>NEXT button</strong> when ready to continue with the instructions. Please also use this time to <strong>adjust your screensize</strong> to ensure the board is easily accessible.</p>'; 

    // "<p>You are <strong>free to use the scratchpad below</strong>, but are <i>not required</i>. To use it: click on a cell to place a piece. Pieces are colored either <span style='color: blue'>blue</span> or <span style='color: red'>red</span>. Colors will switch automatically. If you would like to change colors yourself, press the <strong>SPACE</strong> bar.</p><p>You can undo your last move by pressing <strong>UNDO</strong> or clear the board entire by pressing <strong>CLEAR</strong>.</p>";
    
    // Display the currently selected player
    //var current_player_display = "<p id='current-player-display'></p>";

    var prompt_txt = opener_txt;//+ current_player_display; // + "<p><strong>" + task_questions[task] + "</strong></p>"
    var viz_html =
    `<p></p><br></br>
    <center><div id="gameBoard"></div></center>
    <input type="button" id="undo-btn" type="buttons" class="buttons" value="UNDO"></input><input type="button" id="clear-btn" type="buttons" class="buttons" value="CLEAR"></input></p>`; 
    //         <p>` +
    // //   task_questions[task]["q_fmt"] + 
    //   `</p>`;
    return prompt_txt + viz_html;
}

var simple_question_txt = ""
if (task.includes("fun")) {
  simple_question_txt = "a simple question"
}else{ 
  simple_question_txt = "two simple questions"
}

var pre_instruction_pages = [
  "<p> Welcome! </p> <p> We are conducting an experiment to understand how people think about games. Your answers will be used to inform cognitive science and AI research. </p>" +
    "<p> This experiment should take approximately <strong>" +
    total_time +
    " minutes</strong>. </br></br> You will be compensated at a base rate of $" +
    base_rate +
    "/hour, with an optional bonus to bring the total up to a rate of $" + bonus_rate + "/hr if you try your best throughout the experiment to answer each question.</p>" + 
    "<p>Please set the experiment to full screen.</p>", 
    // "<p>You can receive a bonus to bring your total "
  "<p> We take your compensation and time seriously! The email for the main experimenter is <strong>katiemc@mit.edu</strong>. </br></br> Please write this down now, and email us with your Prolific ID and the subject line <i>Human experiment compensation</i> if you have problems submitting this task, or if it takes much more time than expected. </p>",
  "<p>Please do <i>not</i> use any other Internet source or aid, including internet search, or chatbots — this experiment is designed to measure <i>how people think.</i></p><p>Unfortunately, if we find evidence that you did this, you may not receive the payment for this task.",
  "<p>There are two parts to this experiment. We present the instructions for Part I next. Instructions for a brief Part II will follow after you complete Part I.</p>",
  "<p> In this experiment, you will be <strong>reading short descriptions of board games</strong> and <strong>answering " + simple_question_txt + "</strong> about each game.</p><p>Each game is played by players who take turns by placing pieces on a grid, similar to games like Connect 4, Gomoku (5-in-a-row), or Tic-Tac-Toe.</p>",
  "<p>You will be reading descriptions of games in which the size of the board and the rules for winning vary.</p> <p>We will always show you an example game board from each description. For example, you might read a description like:</p><p><li>The board in this game is a <strong>5 x 5</strong> grid.</li></p><p><li>In this game, the rule is that <strong>the first player to make 3 in a row</strong> wins.</li></p><p>",

  "<p>Then, for each game, your task is to answer: <strong>" +
  task_questions[task]["instruct_fmt"] +
  "</strong>.</p>" +
  "<p>You will answer this question by <strong>dragging a slider.</strong></p>" +
  condition_caveat,

  "<p>Before you answer the question for each game, you will have <i>as much time as you want to think about the game and its rules</i>. You must spend at least 60 seconds thinking about each game.</p>" + 
  "<p>Afer you feel like you understand the game, please press the CONTINUE TO QUESTION to indicate that you are ready to answer the question.</p>", 
  "<p>For each game, you will be shown an <strong>interactive grid</strong> that you can <strong>optionally use as a scratchpad</strong> to think about the game before you answer.</p><p>On the next page, we will show you a demonstration of how this works.</p>",

  ]

  var instruction_pages = [
    "<p>Additionally, you may read descriptions in which you are told that the board size is <strong>infinitely large</strong>.</p><p>In this case, we will show a board with dashed edges to indicate that the borders of the grid should extend beyond what is shown.</p><p>An example (non-interactive) board is shown below.</p><p><img src=" +
    "imgs/rev_inf.png" +
    ' style="max-width:320px; max-height:320px;"></p>',
  "<p><strong>We encourage you to take your time and carefully analyze the game before providing your answer.</strong></p>",

];

var pre_instructions = {
  type: "instructions",
  pages: pre_instruction_pages,
  show_clickable_nav: true,
};


instruction_pages.push(
  "<p> You will see a total of <strong>" +
    num_show +
    " descriptions of games</strong>.</p>"
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
var correct_scratchpad_resp ="For every game, but it is optional.";
var chatbot_affirm = "I affirm that I will not use any other Internet source or aid, including internet search, or chatbots."

var comprehension_check = {
  type: "survey-multi-choice",
  preamble: [
    "<p align='center'>Check your knowledge before you begin. If you don't know the answers, don't worry; we will show you the instructions again.</p>",
  ],
  questions: [
    {
      prompt: "What will you be asked to do in this task?",
      options: [
        correct_task_description,
        "Design new versions of games and then play them.",
        "See pictures of in-progress games and predict the winner.",
      ],
      required: true,
    },

    {
      prompt: "How will you provide your final answer?",
      options: [
        "Typing in a text box.",
        correct_response_indicator,
        "Selecting from a dropdown menu.",
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

    // {
    //   prompt: "When will you be given a scratchpad?",
    //   options: [
    //     "For every game, and it is required to use.",
    //     correct_scratchpad_resp,
    //     "Only for some games, but it is required when presented.",
    //   ],
    //   required: true,
    // }
  ],
  on_finish: function (data) {
    var responses = data.response;
    if (
      responses["Q0"] == correct_task_description &&
      responses["Q1"] == correct_response_indicator &&
      responses["Q2"] == chatbot_affirm
    ) {
      familiarization_check_correct = true;
    } else {
      familiarization_check_correct = false;
    }
  },
};

var familiarization_timeline = [pre_instructions, demoInteractiveBoard, instructions, comprehension_check];

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


var rating_page = {
  type: "multiple-slider",
  preamble: function () {

    var img_pth = jsPsych.timelineVariable("game_img");

    var board_rows = jsPsych.timelineVariable("board_rows");
    var board_cols = jsPsych.timelineVariable("board_cols");

    var opener_txt = `<p><strong>In this game,</strong> imagine you are playing on a <strong>${board_rows} x ${board_cols} board</strong>.</p>`;

    var task = jsPsych.timelineVariable("task");

    var task_txt =
      "<p>The rules for this game are that: <strong>" +
      jsPsych.timelineVariable("win_conditions") +
      "</strong></p>";

    var prompt_txt = opener_txt + task_txt; // + "<p><strong>" + task_questions[task] + "</strong></p>"

    return prompt_txt + "<p>    </p>";
  },
  questions: function(){
    if (task.includes("fun")){
      return [
        {
          prompt: "<p><strong>" + task_questions[task]["q_fmt"] + "</strong></p><p>    </p>",
          name: "response",
          labels: scales[jsPsych.timelineVariable("task")],
          required: true,
        },
      ]
    }else{
      return advantage_sliders

    }
  },
  randomize_question_order: false,
};


var rating_task = {
  // timeline: [stimuli_read, rating_page, interactiveBoard],
  timeline: [interactiveBoard, rating_page],
  timeline_variables: stimuli_batch,
  data: {
    task: jsPsych.timelineVariable("task"),
    board_cols: jsPsych.timelineVariable("board_cols"),
    board_rows: jsPsych.timelineVariable("board_rows"),
    stim_tag: jsPsych.timelineVariable("stim_tag"),
    win_conditions: jsPsych.timelineVariable("win_conditions"),
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
    jsPsych.setProgressBar(curr_progress_bar_value + progress_bar_increase);
  },
};

timeline.push(rating_task);

var create_final_instructions = {
  type: "instructions",
  pages: [
    "<p> You have now completed Part I and are about to start Part II.</p>",
    "<p>In Part II, we now invite you to <strong>create your own game that <i>you would find fun to play</i>.</strong> </p>" +
      '<p> We ask that you provide a <strong>board size</strong> and <strong>win conditions</strong>. You may again optionally use the provided scratchpad as you create your game.</p>' , 
      `<p> Once you have created each game, <strong>you will rate <i>the game you made</i> according to the same prompt</strong>: <i>${task_questions[task]["instruct_fmt"]}</i>.</p>`,
      `<p> After you have created and rated the game, you can continue to the end of the experiment and payment.</p>` + 
      `<p> We reiterate to please NOT use any other Internet source or aid, including internet search, or chatbots.</p>`
  ],
  show_clickable_nav: true,
};
timeline.push(create_final_instructions);

var created_game_size = ""
var created_game_rules = ""

var interactiveBoardCreate = {
  type: "survey-html-form",
  //trial_duration: min_seconds * 1000, // in msec
  html: function () {
    var task = jsPsych.timelineVariable("task");
    var board_rows = jsPsych.timelineVariable("board_rows");
    var board_cols = jsPsych.timelineVariable("board_cols");
    var win_conditions = jsPsych.timelineVariable("win_conditions");

    var opener_txt = "<p>Create a new game variant that <strong>you would find fun to play</strong>!</p>"

    var game_txt = "<p>When you are ready, <i>describe your <strong>new</strong> game</i> in the text boxes provided. First, <strong>specify the board size</strong> (in the form NUM-ROWS x NUM-COLS).</p>" + `<textarea type="text" id="game-entry-size" name="game-size" required="true" cols="60" rows="1"></textarea>` + "<p>Then, <strong>specify the rules to win and any other special conditions of your game</strong>.</p>"  + 
    `<textarea type="text" id="game-entry-conds" name="game-conds" required="true" cols="60" rows="3"></textarea>` 

    var player_select_msg = "<p>You are <strong>free to use the scratchpad below</strong>, but are <i>not required</i>. To use it: click on a cell to place a piece. Pieces are colored either <span style='color: blue'>blue</span> or <span style='color: red'>red</span>. As you place pieces, the colors will automatically alternate. If you instead want to play the same color again, press the <strong>SPACE</strong> bar before placing the piece.</p><p>You can undo your last move by pressing <strong>UNDO</strong> or clear the board entire by pressing <strong>CLEAR</strong>.</p>"; 

    var submit_msg = "<p>When you are happy with your game and ready to submit it, press the <strong>CONTINUE TO QUESTION button</strong>. You must spend <strong>at least 60 seconds</strong> before you are able to proceed.</p>"
    

    var prompt_txt = opener_txt + game_txt + player_select_msg + submit_msg; // + "<p><strong>" + task_questions[task] + "</strong></p>"
    var viz_html =
      `<p></p><br></br>
        <center><div id="gameBoard"></div></center>
        <input type="button" id="undo-btn" type="buttons" class="buttons" value="UNDO"></input><input type="button" id="clear-btn" type="buttons" class="buttons" value="CLEAR"></input></p>`; 
    //         <p>` +
    // //   task_questions[task]["q_fmt"] + 
    //   `</p>`;
    return prompt_txt + viz_html;
  },
  //choices: [" ", "Spacebar"],
  button_label: "CONTINUE TO QUESTION",

  on_load: function() {

    single_sim_board_state = []

    selectedColor = "blue"
    //updateHoverEffect('hover-blue')
    
    
    // document.addEventListener('DOMContentLoaded', () => {
      const gameBoard = document.getElementById('gameBoard');
      // let selectedColor = 'white';
      const clearBtn = document.getElementById("clear-btn");
      const undoBtn = document.getElementById("undo-btn");

      const btn = document.getElementById('jspsych-survey-html-form-next')
      // btn.classList.add("buttons")
      btn.disabled=true
      btn.style.background = "#A8A8A8";
	

		if (official_run){
			var time_delay = min_seconds * 1000
		}else{
			var time_delay = 500
		}
    //var time_delay = 10000

		setTimeout(function(){
			btn.disabled = false;
			console.log('Button Activated')
			btn.style.background = "#112242";
      // document.querySelector('jspsych-survey-html-form-next').src = 'imgB.png'
    }, time_delay);
  
      // // Change this to set the board size
      // const rows = 4;
      // const cols = 9;

      var rows = jsPsych.timelineVariable("board_rows");
      var cols = jsPsych.timelineVariable("board_cols"); 

      rows = "Infinity"
      cols = "Infinity"

      var is_inf = false 
      
      // for now, both cols + row are both inf
      if (rows == "Infinity"){

        rows = 13
        cols = 13

        is_inf = true

      }else{
        rows = parseInt(rows)
        cols = parseInt(cols)
      }

      const maxWidth = window.innerWidth * 0.4;
      const maxHeight = window.innerHeight * 0.4;

      // Set the width of each cell to maintain square shape
      const cellSize = Math.min(maxWidth / cols, maxHeight / rows);
      

      // Initialize the board
      for (let i = 0; i < rows * cols; i++) {
          const cell = document.createElement('div');
          cell.id = i
          //cell.style.backgroundColor = "white"
          cell.classList.add('cell');
          cell.style.width = `${cellSize}px`;
          cell.style.height = `${cellSize}px`;

          if (is_inf){
            if (i < rows) { 
              // Set each border side individually
              cell.style.borderTop = "dashed";           // Remove top border
            }
            if (i % rows == 0){ 
              cell.style.borderLeft=  "dashed"; // none
            }
            if (i % rows == cols - 1){ 
              cell.style.borderRight=  "dashed"; 
            }
            if (i >= rows * (cols - 1)){
              cell.style.borderBottom = "dashed";
            }
            
          }


          gameBoard.appendChild(cell);
      }

      // Update the grid template based on the number of columns
      gameBoard.style.gridTemplateColumns = `repeat(${cols}, ${cellSize}px)`;

      document.querySelectorAll('.cell').forEach(cell => {
        cell.classList.remove('hover-blue', 'hover-red', 'hover-green');
          cell.classList.add('hover-blue');
        
      });



document.addEventListener('click', handleClick)
document.addEventListener('keydown', handleKeyDown)


undoBtn.addEventListener("click", () => {
  console.log("UNDO! last: ", last_cell)
  if (last_cell != ""){
    console.log("reset: ", last_cell)
    last_cell.style.backgroundColor =''; //'white';
    last_cell = ""
    single_sim_board_state.push(["UNDO", "UNDO"])
    if (selectedColor === "red"){
      selectedColor = "blue"
      //updateHoverEffect('hover-blue');
      document.querySelectorAll('.cell').forEach(cell => {
        cell.classList.remove('hover-blue', 'hover-red', 'hover-green');
         cell.classList.add('hover-blue');
      });
    } else if (selectedColor === "blue"){
      selectedColor = "red"
      document.querySelectorAll('.cell').forEach(cell => {
        cell.classList.remove('hover-blue', 'hover-red', 'hover-green');
        cell.classList.add('hover-red');

      });
    }
  }
});

      clearBtn.addEventListener("click", () => {
        document.querySelectorAll('.cell').forEach(cell => {
          cell.style.backgroundColor = '';
        });
        // boardState = Array.from({ length: numRows * numCols }, () => "");
        // currentPlayer = "";
        num_clicks += 1;
        last_cell = ""
        single_sim_board_state.push(["CLEAR", "CLEAR"])
        all_board_states.push(single_sim_board_state);
        single_sim_board_state = [];
        selectedColor = "blue"
      //updateHoverEffect('hover-blue');
      document.querySelectorAll('.cell').forEach(cell => {
        cell.classList.remove('hover-blue', 'hover-red', 'hover-green');
         cell.classList.add('hover-blue');

         

      });
    });
  // });
  

  },
  on_finish: function (data) {
    // help from: https://www.jspsych.org/7.0/reference/jspsych-data/index.html

    console.log("Data: ", data)

    created_game_size = data["response"]["game-size"]
    created_game_rules = data["response"]["game-conds"]
    

    // add final set of accumulated moves (b/c only stored with reset)
    all_board_states.push(single_sim_board_state)

    console.log("num clear clicks: ", num_clicks);
    console.log("board states: ", all_board_states);

    var board_cols = jsPsych.timelineVariable("board_cols")
    var board_rows = jsPsych.timelineVariable("board_rows")
    var stim_tag= jsPsych.timelineVariable("stim_tag")
    var win_conditions = jsPsych.timelineVariable("win_conditions")

    var data = { "num_clear": num_clicks, "board_states": all_board_states, "stim_tag":  stim_tag, "board_cols": board_cols, "board_rows": board_rows, "win_conditions": win_conditions, "page_type": "scratchpad"};
    num_clicks = 0;
    currentPlayer = ""; 
    all_board_states = [];
    jsPsych.data.get().push(data);

    document.removeEventListener("click", handleClick);
    document.removeEventListener("keydown", handleKeyDown);

  },
};


var rating_page_create = {
  type: "multiple-slider",
  preamble: function () {

    var img_pth = jsPsych.timelineVariable("game_img");

    var board_rows = jsPsych.timelineVariable("board_rows");
    var board_cols = jsPsych.timelineVariable("board_cols");

    var opener_txt =  `<p>Now rate the game you just created.</p><p>You created a game with the following board size <strong>${created_game_size}</strong>.<p>With the win conditions: <strong>${created_game_rules}</strong></p>`;

    var prompt_txt = opener_txt; // + "<p><strong>" + task_questions[task] + "</strong></p>"

    return prompt_txt + "<p>    </p>";
  },
  questions: function(){
    if (task.includes("fun")){
      return [
        {
          prompt: "<p><strong>" + task_questions[task]["q_fmt"] + "</strong></p><p>    </p>",
          name: "response",
          labels: scales[jsPsych.timelineVariable("task")],
          required: true,
        },
      ]
    }else{
      return advantage_sliders 

    }
  },
  randomize_question_order: false,
};


var rating_task = {
  // timeline: [stimuli_read, rating_page, interactiveBoard],
  timeline: [interactiveBoard, rating_page],
  timeline_variables: stimuli_batch,
  data: {
    task: jsPsych.timelineVariable("task"),
    board_cols: jsPsych.timelineVariable("board_cols"),
    board_rows: jsPsych.timelineVariable("board_rows"),
    stim_tag: jsPsych.timelineVariable("stim_tag"),
    win_conditions: jsPsych.timelineVariable("win_conditions"),
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
    jsPsych.setProgressBar(curr_progress_bar_value + progress_bar_increase);
  },
};






var rating_task_create = {
  // timeline: [stimuli_read, rating_page, interactiveBoard],
  timeline: [interactiveBoardCreate, rating_page_create],
  timeline_variables: stimuli_batch,
  data: {
    task: jsPsych.timelineVariable("task"),
    // board_cols: jsPsych.timelineVariable("board_cols"),
    // board_rows: jsPsych.timelineVariable("board_rows"),
    // stim_tag: jsPsych.timelineVariable("stim_tag"),
    // win_conditions: jsPsych.timelineVariable("win_conditions"),
    metatask: "full_info_gameplay_scratchpad_autoswitch_create",
  },
  sample: {
    type: "custom",
    fn: function (t) {
      // t = set of indices from 0 to n-1, where n = # of trials in stimuli variable
      // returns a set of indices for trials
      return [0,]; //1, 2];
    },
  },
  on_finish: function () {
    var curr_progress_bar_value = jsPsych.getProgressBarCompleted();
    jsPsych.setProgressBar(curr_progress_bar_value + progress_bar_increase);
  },
};

timeline.push(rating_task_create);







var freq_scale =["No prior experience", 
"Some prior experience playing", 
"Substantial prior experience playing"] 


var experience_page = {
  type: "multiple-slider",
  preamble: function() {
    var prompt_txt = `<p>Thank you for participating in our study! Before finishing, <strong>read the following questions carefully and give your answer on the scales.</strong></p>`;
    return prompt_txt
  },
  questions: [
    {
      prompt: `<p>How much <strong>time did you spend thinking</strong> about each question, on average?</p>`,
      name: "thinking-time",
      labels: ["A few seconds", "Around 1 minute", "Several minutes"], //["30 seconds or less", "Around 1 minute", "2 or more minutes"],
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


	  timeline.push(experience_page)

var questions = [];
if (task.includes("fun")) {
  questions.push({
    prompt:
      "What factors did you consider when deciding whether a game was fun?",
    rows: 5,
    columns: 50,
    required: true,
  });
}
questions.push({
  prompt:
    "How did you come up with answers for the questions? Please explain the strategies you used to think about each game?",
  rows: 5,
  columns: 50,
  required: true,
});
questions.push({
  prompt:
    "What made you decide to use the scratchpad? Was it helpful?",
  rows: 5,
  columns: 50,
  required: true,
});

questions.push({
  prompt:
    "If you used the scratchpad, was there any part of using it that you found difficult, annoying, etc?",
  rows: 5,
  columns: 50,
});
questions.push({
  prompt:
    "Were the questions easier to answer for some games than for others? If so, why?",
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
};
timeline.push(comments_block);

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
      "https://app.prolific.co/submissions/complete?cc=CWMXZWAZ";
  },
  show_progress_bar: true,
  auto_update_progress_bar: false,
});
