"""
FitTrack MCP Server
===================
Comprehensive fitness and rehab tracker for workout logging, hydration management,
nutrition tracking, and evidence-based physical therapy protocols.

Features:
- AC-joint-safe exercise validation
- Hyperhidrosis-aware hydration calculations
- Late-meal guardrails (9pm+ warnings)
- RPE-based progression tracking
- Evidence-based PT protocols for 6 conditions
"""

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, List, Dict, Any, Literal
from enum import Enum
from datetime import datetime, time
import json

# Initialize MCP server
mcp = FastMCP("fittrack_mcp")

# Constants
CHARACTER_LIMIT = 25000
LATE_MEAL_WARNING_HOUR = 21  # 9 PM

# AC-Joint Safe Exercises
AC_JOINT_SAFE_EXERCISES = {
    "pressing": [
        "Landmine Press",
        "Scapular Plane DB Press (30-45° angle)",
        "Neutral Grip DB Press",
        "Low Incline Press (<30°)",
        "Floor Press"
    ],
    "pulling": [
        "Face Pulls",
        "Cable Rows (all variations)",
        "DB Rows",
        "Lat Pulldowns (neutral/underhand grip)",
        "Scapular Retraction Exercises"
    ],
    "lower_body_standing": [
        "Goblet Squats",
        "Split Squats",
        "Single-Leg RDL",
        "Landmine Squats",
        "Step-ups"
    ],
    "serratus_lower_trap_focus": [
        "Serratus Wall Slides",
        "Bear Crawls",
        "Scapular Push-ups",
        "Lower Trap Y-Raises (prone)",
        "Prone T-Raises",
        "Band Pull-aparts (varied angles)"
    ],
    "core_standing": [
        "Pallof Press",
        "Landmine Rotations",
        "Anti-Rotation Band Work",
        "Single-Leg Deadlift (balance component)"
    ]
}

# Unsafe exercises for AC joint
AC_JOINT_UNSAFE = [
    "Bench Press (flat)", 
    "Overhead Press (strict)",
    "Dips",
    "Wide-grip exercises",
    "Heavy cross-body movements"
]

# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class IntensityLevel(str, Enum):
    """RPE-based intensity levels"""
    RPE_6 = "6 - Very light"
    RPE_7 = "7 - Light"
    RPE_8 = "8 - Moderate"
    RPE_9 = "9 - Hard"
    RPE_10 = "10 - Maximum effort"

class ResponseFormat(str, Enum):
    """Output format options"""
    MARKDOWN = "markdown"
    JSON = "json"

class ExerciseCategory(str, Enum):
    """Exercise categories for filtering"""
    PRESSING = "pressing"
    PULLING = "pulling"
    LOWER_BODY = "lower_body"
    SERRATUS_FOCUS = "serratus_lower_trap"
    CORE = "core"
    REHAB = "rehab"

class RehabCondition(str, Enum):
    """Available rehab protocols"""
    AC_JOINT = "ac_joint_arthritis"
    BICEP = "bicep_tendonitis"
    CERVICAL = "cervical_spine_arthritis"
    SCAPULAR_WINGING = "scapular_winging"
    ANKLE_POST_SURGERY = "ankle_post_surgery"
    MENISCUS_POST_SURGERY = "meniscus_post_surgery"

class LogWorkoutInput(BaseModel):
    """Input for logging workout sessions"""
    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True)
    
    exercise_name: str = Field(..., description="Name of exercise (e.g., 'Landmine Press', 'Face Pulls')", min_length=1)
    sets: int = Field(..., description="Number of sets completed", ge=1, le=10)
    reps: int = Field(..., description="Reps per set", ge=1, le=50)
    weight_lbs: Optional[float] = Field(None, description="Weight used in pounds", ge=0)
    rpe: IntensityLevel = Field(..., description="Rate of Perceived Exertion (6-10 scale)")
    notes: Optional[str] = Field(None, description="Additional notes (form checks, pain, etc.)", max_length=500)
    response_format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN, description="Output format")

class CalculateHydrationInput(BaseModel):
    """Input for hydration calculations (hyperhidrosis-aware)"""
    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True)
    
    workout_duration_minutes: int = Field(..., description="Workout duration in minutes", ge=15, le=240)
    intensity: IntensityLevel = Field(..., description="Workout intensity (RPE scale)")
    ambient_temp_f: int = Field(default=72, description="Ambient temperature in Fahrenheit", ge=40, le=110)
    sweat_rate_lbs_per_hour: Optional[float] = Field(
        default=2.5,
        description="Your measured sweat rate (lbs/hour). Default 2.5 for heavy sweaters",
        ge=1.0,
        le=5.0
    )
    response_format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN, description="Output format")

class LogNutritionInput(BaseModel):
    """Input for meal logging with late-meal guardrails"""
    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True)
    
    meal_time: str = Field(..., description="Meal time in HH:MM format (24-hour)", pattern=r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$')
    meal_description: str = Field(..., description="Brief meal description", min_length=1, max_length=200)
    protein_g: Optional[int] = Field(None, description="Protein in grams", ge=0, le=300)
    carbs_g: Optional[int] = Field(None, description="Carbs in grams", ge=0, le=500)
    fat_g: Optional[int] = Field(None, description="Fat in grams", ge=0, le=200)
    calories: Optional[int] = Field(None, description="Total calories", ge=0, le=5000)
    response_format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN, description="Output format")

class GetExerciseLibraryInput(BaseModel):
    """Input for exercise library queries"""
    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True)
    
    category: Optional[ExerciseCategory] = Field(None, description="Filter by exercise category")
    search_term: Optional[str] = Field(None, description="Search for specific exercises", max_length=50)
    response_format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN, description="Output format")

class GetRehabProtocolInput(BaseModel):
    """Input for PT/rehab protocol queries"""
    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True)
    
    condition: RehabCondition = Field(..., description="Rehab condition to get protocol for")
    phase: Optional[int] = Field(None, description="Specific phase number (1-4)", ge=1, le=4)
    response_format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN, description="Output format")

# ============================================================================
# REHAB PROTOCOL DATABASE
# ============================================================================

REHAB_PROTOCOLS = {
    "ac_joint_arthritis": {
        "name": "AC Joint Arthritis Rehabilitation",
        "overview": "Evidence-based protocol for managing AC joint osteoarthritis. Focus on scapular stabilization, pain reduction, and avoiding overhead/cross-body movements.",
        "phases": [
            {
                "phase": 1,
                "name": "Pain Control & Initial Mobility (Weeks 1-3)",
                "goals": ["Reduce inflammation", "Restore pain-free ROM", "Begin gentle scapular activation"],
                "exercises": [
                    {"name": "Pendulum exercises", "sets": 3, "reps": 20, "frequency": "3x/day", "notes": "Gentle, pain-free circles"},
                    {"name": "Supine shoulder flexion with dowel", "sets": 3, "reps": 15, "frequency": "Daily", "notes": "Use unaffected arm to assist"},
                    {"name": "Scapular retraction (isometric)", "sets": 3, "reps": "10-sec hold", "frequency": "2x/day", "notes": "Squeeze shoulder blades together"},
                    {"name": "Wall slides", "sets": 3, "reps": 10, "frequency": "Daily", "notes": "Keep back flat against wall"},
                ],
                "restrictions": ["Avoid overhead reaching", "No cross-body movements", "Limit weight-bearing through arm"]
            },
            {
                "phase": 2,
                "name": "Strengthening & Scapular Control (Weeks 3-6)",
                "goals": ["Improve scapular muscle balance", "Progress ROM", "Begin rotator cuff strengthening"],
                "exercises": [
                    {"name": "Serratus anterior wall slides", "sets": 3, "reps": 12, "frequency": "Daily", "notes": "Focus on protraction"},
                    {"name": "Lower trap Y-raises (prone)", "sets": 3, "reps": 12, "frequency": "3x/week", "notes": "Light weight, thumbs up"},
                    {"name": "Face pulls", "sets": 3, "reps": 15, "frequency": "3x/week", "notes": "Safe AC joint exercise"},
                    {"name": "External rotation (side-lying)", "sets": 3, "reps": 15, "frequency": "3x/week", "notes": "Light resistance"},
                    {"name": "Scapular plane elevation", "sets": 3, "reps": 12, "frequency": "3x/week", "notes": "30-45° angle, not directly overhead"},
                ],
                "restrictions": ["Keep elevation < 90° initially", "Avoid bench press/dips"]
            },
            {
                "phase": 3,
                "name": "Progressive Loading (Weeks 6-12)",
                "goals": ["Increase strength", "Improve endurance", "Return to functional activities"],
                "exercises": [
                    {"name": "Landmine press", "sets": 3, "reps": 10, "frequency": "2-3x/week", "notes": "AC-joint safe pressing"},
                    {"name": "Cable rows (all variations)", "sets": 3, "reps": 12, "frequency": "2-3x/week", "notes": "Maintain scapular control"},
                    {"name": "Neutral-grip DB press", "sets": 3, "reps": 10, "frequency": "2x/week", "notes": "Scapular plane"},
                    {"name": "TRX/suspension trainer rows", "sets": 3, "reps": 15, "frequency": "2x/week", "notes": "Body weight progression"},
                    {"name": "Bear crawls", "sets": 3, "reps": "30 sec", "frequency": "2x/week", "notes": "Serratus activation"},
                ],
                "restrictions": ["Progress weight slowly", "Monitor for pain flare-ups"]
            },
            {
                "phase": 4,
                "name": "Return to Training (Week 12+)",
                "goals": ["Maintain strength gains", "Prevent reinjury", "Full functional capacity"],
                "exercises": [
                    {"name": "Continue Phase 3 exercises", "sets": 3, "reps": "8-12", "frequency": "2-3x/week", "notes": "Progressive overload via RPE"},
                    {"name": "Sport-specific movements", "sets": 3, "reps": "Varies", "frequency": "As needed", "notes": "Gradually reintroduce activities"},
                ],
                "restrictions": ["Permanently avoid flat bench press", "Minimize cross-body loading"]
            }
        ],
        "key_principles": [
            "Scapular stabilization is foundation",
            "Avoid provocative movements (overhead press, wide-grip bench)",
            "Progressive loading matched to tissue tolerance",
            "RPE-based progression (start RPE 6-7, progress to 8-9)"
        ]
    },
    
    "bicep_tendonitis": {
        "name": "Bicep Tendonitis Rehabilitation",
        "overview": "Multimodal approach: eccentric loading, manual therapy, scapular strengthening. Progressive loading matched to pain/irritability.",
        "phases": [
            {
                "phase": 1,
                "name": "Pain Management & Load Tolerance (Weeks 1-2)",
                "goals": ["Reduce pain/inflammation", "Avoid tendon aggravation", "Begin isometric training"],
                "exercises": [
                    {"name": "Isometric bicep hold (90° elbow)", "sets": 3, "reps": "30-45 sec", "frequency": "Daily", "notes": "Sub-maximal, pain-free"},
                    {"name": "Scapular retraction", "sets": 3, "reps": 15, "frequency": "2x/day", "notes": "Reduce anterior shoulder stress"},
                    {"name": "Pec minor stretch (doorway)", "sets": 3, "reps": "30 sec", "frequency": "2x/day", "notes": "Open anterior thorax"},
                    {"name": "Ice after activity", "sets": 1, "reps": "15 min", "frequency": "As needed", "notes": "Reduce inflammation"},
                ],
                "restrictions": ["Avoid overhead activities", "No heavy lifting", "Limit cross-body movements"]
            },
            {
                "phase": 2,
                "name": "Eccentric Loading & Mobility (Weeks 2-6)",
                "goals": ["Progressive tendon loading", "Improve tissue capacity", "Restore ROM"],
                "exercises": [
                    {"name": "Eccentric bicep curls", "sets": 3, "reps": 10, "frequency": "3x/week", "notes": "Slow 4-5 sec negative, light weight"},
                    {"name": "Bicep stretch (arm extended)", "sets": 3, "reps": "30 sec", "frequency": "Daily", "notes": "Gentle, pain-free"},
                    {"name": "Shoulder flexion ROM", "sets": 3, "reps": 15, "frequency": "Daily", "notes": "Progress overhead gradually"},
                    {"name": "Rotator cuff strengthening", "sets": 3, "reps": 12, "frequency": "3x/week", "notes": "Light bands/dumbbells"},
                ],
                "restrictions": ["Avoid explosive movements", "Long-lever arm exercises only with clearance"]
            },
            {
                "phase": 3,
                "name": "Progressive Resistance (Weeks 6-12)",
                "goals": ["Build tendon resilience", "Return to functional strength", "Improve shoulder complex coordination"],
                "exercises": [
                    {"name": "Heavy slow resistance curls", "sets": 4, "reps": 6-8, "frequency": "2-3x/week", "notes": "Controlled tempo, full ROM"},
                    {"name": "Hammer curls", "sets": 3, "reps": 10, "frequency": "2x/week", "notes": "Neutral grip reduces stress"},
                    {"name": "Scapular strengthening (all planes)", "sets": 3, "reps": 12, "frequency": "3x/week", "notes": "Rows, Y-raises, T-raises"},
                    {"name": "Closed-chain exercises", "sets": 3, "reps": 10, "frequency": "2x/week", "notes": "Push-up variations, planks"},
                ],
                "restrictions": ["Monitor pain/irritability", "Adjust load if symptoms increase"]
            },
            {
                "phase": 4,
                "name": "Return to Activity (Week 12+)",
                "goals": ["Maintain tendon health", "Full functional capacity", "Prevent recurrence"],
                "exercises": [
                    {"name": "Continue Phase 3 exercises", "sets": 3, "reps": "8-12", "frequency": "2-3x/week", "notes": "Maintenance program"},
                    {"name": "Sport-specific training", "sets": "Varies", "reps": "Varies", "frequency": "As needed", "notes": "Gradual return"},
                ],
                "restrictions": ["Avoid sudden increases in training volume"]
            }
        ],
        "key_principles": [
            "Eccentric exercise is most effective intervention",
            "Progressive loading matched to tissue capacity",
            "Address scapular dysfunction (common comorbidity)",
            "Consider dry needling if available"
        ]
    },

    "cervical_spine_arthritis": {
        "name": "Cervical Spine Arthritis & Cervical Radiculopathy",
        "overview": "Exercise therapy, manual therapy, and postural training. Focus on deep neck flexor/extensor strengthening and ROM.",
        "phases": [
            {
                "phase": 1,
                "name": "Pain Reduction & Postural Awareness (Weeks 1-2)",
                "goals": ["Reduce pain/inflammation", "Improve posture", "Begin gentle ROM"],
                "exercises": [
                    {"name": "Chin tucks", "sets": 3, "reps": 15, "frequency": "3-4x/day", "notes": "Tuck chin without flexing head forward"},
                    {"name": "Isometric neck flexion", "sets": 3, "reps": "10-sec hold", "frequency": "2x/day", "notes": "Press hand against forehead, resist"},
                    {"name": "Isometric neck extension", "sets": 3, "reps": "10-sec hold", "frequency": "2x/day", "notes": "Press hand against back of head"},
                    {"name": "Gentle neck rotation", "sets": 3, "reps": 10, "frequency": "Daily", "notes": "Pain-free ROM only"},
                    {"name": "Postural correction cues", "sets": "Throughout day", "reps": "N/A", "frequency": "Hourly", "notes": "Neutral spine, avoid forward head posture"},
                ],
                "restrictions": ["Avoid prolonged neck flexion (looking down at phone)", "No heavy lifting overhead"]
            },
            {
                "phase": 2,
                "name": "Strengthening & Mobility (Weeks 2-6)",
                "goals": ["Strengthen deep neck flexors/extensors", "Improve ROM all planes", "Build endurance"],
                "exercises": [
                    {"name": "Deep neck flexor training", "sets": 3, "reps": "20-30 sec", "frequency": "Daily", "notes": "Supine, nod head without lifting"},
                    {"name": "Neck extension strengthening", "sets": 3, "reps": 12, "frequency": "3x/week", "notes": "Prone or seated with resistance"},
                    {"name": "Cervical rotation with resistance", "sets": 3, "reps": 10, "frequency": "3x/week", "notes": "Use light band"},
                    {"name": "Scapular retraction rows", "sets": 3, "reps": 15, "frequency": "3x/week", "notes": "Reduce cervical load"},
                    {"name": "Thoracic spine extension", "sets": 3, "reps": 10, "frequency": "Daily", "notes": "Foam roller or prone cobras"},
                ],
                "restrictions": ["Avoid end-range extension if radiculopathy present"]
            },
            {
                "phase": 3,
                "name": "Progressive Loading & Function (Weeks 6-12)",
                "goals": ["Increase strength/endurance", "Return to normal activities", "Improve cardiovascular fitness"],
                "exercises": [
                    {"name": "Neck endurance training (isometric)", "sets": 3, "reps": "60+ sec", "frequency": "3x/week", "notes": "Multiple angles"},
                    {"name": "Upper trap/levator scapulae strengthening", "sets": 3, "reps": 12, "frequency": "2x/week", "notes": "Shrugs with control"},
                    {"name": "Postural strengthening (standing)", "sets": 3, "reps": 15, "frequency": "3x/week", "notes": "Wall angels, band pull-aparts"},
                    {"name": "Cardiovascular training", "sets": 1, "reps": "20-30 min", "frequency": "3-5x/week", "notes": "Walking, cycling (proper neck position)"},
                ],
                "restrictions": ["Maintain neutral spine during all activities"]
            },
            {
                "phase": 4,
                "name": "Maintenance & Prevention (Week 12+)",
                "goals": ["Sustain gains", "Prevent recurrence", "Optimize ergonomics"],
                "exercises": [
                    {"name": "Continue Phase 3 exercises", "sets": 2-3, "reps": "10-15", "frequency": "2-3x/week", "notes": "Maintenance program"},
                    {"name": "Ergonomic adjustments", "sets": "N/A", "reps": "N/A", "frequency": "Ongoing", "notes": "Workstation setup, sleep position"},
                ],
                "restrictions": ["Avoid prolonged static postures"]
            }
        ],
        "key_principles": [
            "Deep neck flexor strengthening is key",
            "Address thoracic spine mobility (often restricted)",
            "Postural correction crucial for long-term success",
            "Manual therapy effective adjunct (if available)"
        ]
    },

    "scapular_winging": {
        "name": "Scapular Winging Rehabilitation",
        "overview": "Conservative management for serratus anterior, trapezius, or rhomboid weakness. Focus on scapular stabilization, ROM maintenance, and gradual strengthening.",
        "phases": [
            {
                "phase": 1,
                "name": "Protection & ROM (Weeks 1-6)",
                "goals": ["Maintain ROM", "Prevent contracture", "Avoid stretching paralyzed muscle"],
                "exercises": [
                    {"name": "Supine shoulder flexion (passive)", "sets": 3, "reps": 15, "frequency": "Daily", "notes": "Body weight prevents winging"},
                    {"name": "Shoulder rolls", "sets": 3, "reps": 15, "frequency": "2x/day", "notes": "Gentle, pain-free"},
                    {"name": "Scapular protraction (wall)", "sets": 3, "reps": 12, "frequency": "Daily", "notes": "Push-plus position"},
                    {"name": "Avoid serratus stretching", "sets": "N/A", "reps": "N/A", "frequency": "N/A", "notes": "Do NOT stretch affected muscle"},
                ],
                "restrictions": ["No overhead activities", "Avoid heavy lifting", "Consider scapular brace (if tolerated)"]
            },
            {
                "phase": 2,
                "name": "Reinnervation & Initial Strengthening (Weeks 6-24)",
                "goals": ["Promote nerve recovery", "Begin strengthening after reinnervation signs", "Improve motor control"],
                "exercises": [
                    {"name": "Serratus wall slides (if reinnervation present)", "sets": 3, "reps": 10, "frequency": "Daily", "notes": "Only after muscle activation"},
                    {"name": "Scapular push-ups (modified)", "sets": 3, "reps": 8, "frequency": "3x/week", "notes": "Wall or elevated surface"},
                    {"name": "Bear crawl hold", "sets": 3, "reps": "15-30 sec", "frequency": "3x/week", "notes": "Serratus activation"},
                    {"name": "Compensatory strengthening (trap/rhomboids)", "sets": 3, "reps": 12, "frequency": "3x/week", "notes": "Support scapular position"},
                ],
                "restrictions": ["Progress only with evidence of reinnervation", "Avoid overstressing recovering muscle"]
            },
            {
                "phase": 3,
                "name": "Progressive Strengthening (6-24 months)",
                "goals": ["Build strength/endurance", "Improve functional capacity", "Compensatory strengthening"],
                "exercises": [
                    {"name": "Push-up progressions", "sets": 3, "reps": "As able", "frequency": "3x/week", "notes": "Elevate to floor push-ups"},
                    {"name": "Rows (all variations)", "sets": 3, "reps": 12, "frequency": "3x/week", "notes": "Strengthen scapular retractors"},
                    {"name": "Plank variations", "sets": 3, "reps": "30-60 sec", "frequency": "3x/week", "notes": "Serratus endurance"},
                    {"name": "Upper trap/levator scapulae work", "sets": 3, "reps": 12, "frequency": "2x/week", "notes": "Compensatory muscles"},
                ],
                "restrictions": ["Recovery is slow (6-24 months)", "Some cases may not fully recover"]
            },
            {
                "phase": 4,
                "name": "Functional Return (24+ months or surgical consideration)",
                "goals": ["Maximize function", "Determine need for surgical intervention", "Adaptations"],
                "exercises": [
                    {"name": "Continue Phase 3 exercises", "sets": 3, "reps": "10-15", "frequency": "2-3x/week", "notes": "Maintenance"},
                    {"name": "Task-specific training", "sets": "Varies", "reps": "Varies", "frequency": "As needed", "notes": "Functional activities"},
                ],
                "restrictions": ["If no recovery by 24 months, surgical options considered"]
            }
        ],
        "key_principles": [
            "Conservative management for 6-24 months minimum",
            "Do NOT stretch paralyzed muscle (impairs recovery)",
            "Strengthen compensatory muscles",
            "Scapular brace may help but compliance often poor",
            "Spontaneous recovery 21-78% depending on cause"
        ]
    },

    "ankle_post_surgery": {
        "name": "Post-Ankle Surgery Rehabilitation",
        "overview": "Phased protocol for ankle ORIF, ligament repair, or arthroscopy. Progressive weight-bearing, ROM, and strengthening.",
        "phases": [
            {
                "phase": 1,
                "name": "Immediate Post-Op (Weeks 0-6)",
                "goals": ["Control swelling", "Protect healing structures", "Maintain proximal strength"],
                "exercises": [
                    {"name": "Ankle pumps", "sets": 3, "reps": 20, "frequency": "Every 2 hours", "notes": "Toe up, toe down—reduce swelling"},
                    {"name": "Isometric quad sets", "sets": 3, "reps": 15, "frequency": "3x/day", "notes": "Maintain quad strength"},
                    {"name": "Straight leg raises", "sets": 3, "reps": 15, "frequency": "2x/day", "notes": "Hip flexor strength"},
                    {"name": "Towel stretches (gentle)", "sets": 3, "reps": "30 sec", "frequency": "Daily", "notes": "Begin plantar/dorsiflexion ROM"},
                    {"name": "Ice/elevation", "sets": "Multiple", "reps": "15-20 min", "frequency": "3-4x/day", "notes": "Control swelling"},
                ],
                "restrictions": ["Non-weight-bearing (NWB) per MD orders", "Boot/cast immobilization", "No driving"]
            },
            {
                "phase": 2,
                "name": "Progressive Weight-Bearing (Weeks 6-12)",
                "goals": ["Progress to full weight-bearing", "Restore ROM", "Begin strengthening"],
                "exercises": [
                    {"name": "Gait training with assistive device", "sets": "Multiple", "reps": "As tolerated", "frequency": "Daily", "notes": "Partial → full WB"},
                    {"name": "AAROM (alphabet tracing)", "sets": 3, "reps": "3x alphabet", "frequency": "2x/day", "notes": "Improve ROM"},
                    {"name": "Calf raises (bilateral)", "sets": 3, "reps": 10, "frequency": "Daily", "notes": "Progress to single-leg"},
                    {"name": "Theraband resistance (all planes)", "sets": 3, "reps": 15, "frequency": "Daily", "notes": "DF, PF, inversion, eversion"},
                    {"name": "Balance exercises (bilateral)", "sets": 3, "reps": "30 sec", "frequency": "Daily", "notes": "Single-leg as able"},
                ],
                "restrictions": ["No running/jumping", "Protected WB per protocol"]
            },
            {
                "phase": 3,
                "name": "Strengthening & Proprioception (Weeks 12-16)",
                "goals": ["Build strength/endurance", "Improve balance/proprioception", "Prepare for functional activities"],
                "exercises": [
                    {"name": "Single-leg calf raises", "sets": 3, "reps": 15, "frequency": "3x/week", "notes": "Full ankle strength"},
                    {"name": "Single-leg balance (unstable surface)", "sets": 3, "reps": "60 sec", "frequency": "Daily", "notes": "Progress to eyes closed"},
                    {"name": "Lateral band walks", "sets": 3, "reps": 15, "frequency": "3x/week", "notes": "Hip/ankle stability"},
                    {"name": "Step-ups/step-downs", "sets": 3, "reps": 12, "frequency": "3x/week", "notes": "Eccentric control"},
                    {"name": "Heel-toe walking", "sets": 3, "reps": "20 steps", "frequency": "Daily", "notes": "ROM + balance"},
                ],
                "restrictions": ["No high-impact activities yet"]
            },
            {
                "phase": 4,
                "name": "Return to Activity (Week 16+)",
                "goals": ["Return to sport/activity", "Prevent reinjury", "Full functional capacity"],
                "exercises": [
                    {"name": "Running progression", "sets": "Varies", "reps": "Varies", "frequency": "Per protocol", "notes": "Walk/jog intervals → full run"},
                    {"name": "Agility drills", "sets": 3, "reps": "Varies", "frequency": "3x/week", "notes": "Cone drills, cutting"},
                    {"name": "Plyometrics (box jumps, hops)", "sets": 3, "reps": 10, "frequency": "2x/week", "notes": "Power development"},
                    {"name": "Sport-specific training", "sets": "Varies", "reps": "Varies", "frequency": "As needed", "notes": "Gradual return"},
                ],
                "restrictions": ["Functional testing (hop tests) before full return", "Brace/taping as needed"]
            }
        ],
        "key_principles": [
            "Early ankle mobilization (post-immobilization) improves outcomes",
            "Progressive weight-bearing protocols vary by surgery type",
            "Proprioception training critical for reinjury prevention",
            "Expect 4-6 months for full return to high-impact activities"
        ]
    },

    "meniscus_post_surgery": {
        "name": "Post-Meniscus Surgery Rehabilitation",
        "overview": "Protocol varies by tear type (repair vs. partial meniscectomy). Repairs require protected weight-bearing and slower ROM progression.",
        "phases": [
            {
                "phase": 1,
                "name": "Immediate Post-Op - MENISCUS REPAIR (Weeks 0-3)",
                "goals": ["Protect repair", "Control swelling", "Maintain quad strength"],
                "exercises": [
                    {"name": "Quad sets", "sets": 3, "reps": 20, "frequency": "3x/day", "notes": "Isometric quad activation"},
                    {"name": "Straight leg raises", "sets": 3, "reps": 15, "frequency": "2x/day", "notes": "Keep knee straight"},
                    {"name": "Hamstring sets", "sets": 3, "reps": 15, "frequency": "2x/day", "notes": "Gentle isometric"},
                    {"name": "Ankle pumps", "sets": 3, "reps": 20, "frequency": "Hourly", "notes": "Prevent DVT"},
                    {"name": "PROM/AAROM (0-90°)", "sets": 3, "reps": 10, "frequency": "Daily", "notes": "Limited ROM initially"},
                ],
                "restrictions": ["Toe-touch weight-bearing only (repair)", "Brace locked in extension", "ROM limited to 90° flexion"]
            },
            {
                "phase": 2,
                "name": "Protected Weight-Bearing - REPAIR (Weeks 3-8)",
                "goals": ["Progress WB gradually", "Increase ROM to 125°", "Begin closed-chain exercises"],
                "exercises": [
                    {"name": "Gait training (progressive WB)", "sets": "Multiple", "reps": "As tolerated", "frequency": "Daily", "notes": "25% → 50% → 75% → full WB"},
                    {"name": "Heel slides", "sets": 3, "reps": 15, "frequency": "Daily", "notes": "Progress ROM"},
                    {"name": "Mini-squats (bilateral)", "sets": 3, "reps": 12, "frequency": "3x/week", "notes": "0-45° flexion"},
                    {"name": "Leg press (light)", "sets": 3, "reps": 15, "frequency": "2x/week", "notes": "Closed-chain strengthening"},
                    {"name": "Stationary bike (low resistance)", "sets": 1, "reps": "10-15 min", "frequency": "Daily", "notes": "ROM + cardiovascular"},
                ],
                "restrictions": ["No open-chain quad exercises yet", "Avoid deep squatting", "No pivoting/twisting"]
            },
            {
                "phase": 3,
                "name": "Strengthening & ROM - REPAIR (Weeks 8-16)",
                "goals": ["Full ROM", "Progressive strengthening", "Improve proprioception"],
                "exercises": [
                    {"name": "Full ROM exercises", "sets": 3, "reps": 15, "frequency": "Daily", "notes": "0-135°+ flexion"},
                    {"name": "Leg press (progressive load)", "sets": 3, "reps": 12, "frequency": "3x/week", "notes": "Build quad strength"},
                    {"name": "Step-ups", "sets": 3, "reps": 12, "frequency": "3x/week", "notes": "Functional strength"},
                    {"name": "Single-leg balance", "sets": 3, "reps": "60 sec", "frequency": "Daily", "notes": "Progress to unstable surface"},
                    {"name": "Hamstring curls", "sets": 3, "reps": 15, "frequency": "3x/week", "notes": "Posterior chain"},
                    {"name": "Open-chain quad exercises (light)", "sets": 3, "reps": 12, "frequency": "2x/week", "notes": "After 12 weeks"},
                ],
                "restrictions": ["No running until week 12+", "No cutting/jumping until cleared"]
            },
            {
                "phase": 4,
                "name": "Return to Sport - REPAIR (4-6+ months)",
                "goals": ["Return to full activity", "Pass functional tests", "Prevent reinjury"],
                "exercises": [
                    {"name": "Running progression", "sets": "Varies", "reps": "Varies", "frequency": "Per protocol", "notes": "Gradual return"},
                    {"name": "Agility drills", "sets": 3, "reps": "Varies", "frequency": "3x/week", "notes": "Cutting, pivoting"},
                    {"name": "Plyometrics", "sets": 3, "reps": 10, "frequency": "2-3x/week", "notes": "Box jumps, depth jumps"},
                    {"name": "Sport-specific training", "sets": "Varies", "reps": "Varies", "frequency": "As needed", "notes": "Full clearance from MD"},
                ],
                "restrictions": ["Must pass hop tests (>90% limb symmetry)", "Minimum 4-6 months for repair"]
            }
        ],
        "additional_notes": {
            "partial_meniscectomy": "Faster protocol—full WB immediately, ROM unlimited, return to sport 4-8 weeks",
            "repair_variations": "Radial/root tears require 6-9 months due to disrupted hoop stress"
        },
        "key_principles": [
            "Repair vs. meniscectomy = vastly different timelines",
            "Protected WB for repairs (hoop stress preservation)",
            "ROM progression slower for repairs to avoid gap formation",
            "~90% return to sport rate for isolated repairs"
        ]
    }
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def check_ac_joint_safety(exercise_name: str) -> Dict[str, Any]:
    """Check if exercise is AC-joint safe"""
    exercise_lower = exercise_name.lower()
    
    # Check if explicitly unsafe
    for unsafe in AC_JOINT_UNSAFE:
        if unsafe.lower() in exercise_lower:
            return {
                "safe": False,
                "reason": f"❌ {exercise_name} is NOT recommended for AC joint arthritis. Avoid wide-grip and flat bench pressing."
            }
    
    # Check if explicitly safe
    for category, exercises in AC_JOINT_SAFE_EXERCISES.items():
        for safe_ex in exercises:
            if safe_ex.lower() in exercise_lower:
                return {
                    "safe": True,
                    "reason": f"✅ {exercise_name} is AC-joint safe ({category} category)."
                }
    
    # Unknown exercise
    return {
        "safe": None,
        "reason": f"⚠️  {exercise_name} not in database. Verify with these principles: avoid flat bench press, wide-grip movements, strict overhead press. Prefer scapular-plane pressing (30-45° angle), neutral grips, and landmine variations."
    }

def calculate_hydration_needs(
    duration_min: int,
    intensity: str,
    temp_f: int,
    sweat_rate: float
) -> Dict[str, Any]:
    """Calculate hydration needs for hyperhidrosis"""
    # Base sweat rate adjustment by intensity
    intensity_multipliers = {
        "6 - Very light": 0.7,
        "7 - Light": 0.8,
        "8 - Moderate": 1.0,
        "9 - Hard": 1.3,
        "10 - Maximum effort": 1.5
    }
    
    # Temperature adjustment
    temp_multiplier = 1.0
    if temp_f > 80:
        temp_multiplier = 1.2
    elif temp_f > 90:
        temp_multiplier = 1.4
    
    # Calculate fluid loss
    adjusted_sweat_rate = sweat_rate * intensity_multipliers.get(intensity, 1.0) * temp_multiplier
    fluid_loss_lbs = adjusted_sweat_rate * (duration_min / 60)
    fluid_loss_oz = fluid_loss_lbs * 16  # 1 lb = ~16 oz
    
    # Sodium recommendation (3-5g/day for hyperhidrosis, scaled to workout)
    sodium_mg = int((duration_min / 60) * 1500)  # ~1.5g/hour during training
    
    # Replacement protocol (100-150% of loss over 2-4 hours)
    replace_oz_min = fluid_loss_oz
    replace_oz_max = fluid_loss_oz * 1.5
    
    return {
        "sweat_rate_adjusted": round(adjusted_sweat_rate, 2),
        "fluid_loss_lbs": round(fluid_loss_lbs, 2),
        "fluid_loss_oz": round(fluid_loss_oz, 1),
        "replace_oz_range": f"{round(replace_oz_min, 1)}-{round(replace_oz_max, 1)}",
        "sodium_mg": sodium_mg,
        "timing": "Distribute over 2-4 hours post-workout",
        "tips": [
            "Include potassium-rich foods (banana, potato)",
            "Magnesium supplement if cramping",
            "Monitor urine color (pale yellow = good hydration)",
            f"Pre-workout: 16-20 oz 2 hours before, 8-10 oz 15 min before"
        ]
    }

def check_late_meal_warning(meal_time_str: str) -> Optional[str]:
    """Check if meal is after 9pm and provide guardrail warnings"""
    hour = int(meal_time_str.split(':')[0])
    minute = int(meal_time_str.split(':')[1])
    
    if hour >= LATE_MEAL_WARNING_HOUR or hour < 6:  # 9pm - 6am
        warnings = [
            "🚨 **LATE MEAL GUARDRAIL TRIGGERED**",
            f"   - Eating at {meal_time_str} may interfere with sleep quality",
            "   - Consider: 10-15 min walk after eating",
            "   - Keep portions lighter than usual",
            "   - Avoid high-fat, high-acid foods",
            "   - Next time: earlier protein snack (7-8pm) to prevent late binge"
        ]
        return "\n".join(warnings)
    return None

def format_rehab_protocol(condition: str, phase_num: Optional[int], format_type: str) -> str:
    """Format rehab protocol for output"""
    protocol = REHAB_PROTOCOLS.get(condition)
    if not protocol:
        return json.dumps({"error": "Protocol not found"}, indent=2)
    
    if format_type == "json":
        if phase_num:
            return json.dumps({
                "condition": protocol["name"],
                "phase": protocol["phases"][phase_num - 1]
            }, indent=2)
        return json.dumps(protocol, indent=2)
    
    # Markdown format
    output = [f"# {protocol['name']}\n"]
    output.append(f"**Overview:** {protocol['overview']}\n")
    
    if phase_num:
        # Single phase
        phase = protocol["phases"][phase_num - 1]
        output.append(f"## Phase {phase['phase']}: {phase['name']}\n")
        output.append(f"**Goals:**\n" + "\n".join(f"  - {g}" for g in phase['goals']))
        output.append(f"\n**Exercises:**\n")
        for ex in phase['exercises']:
            output.append(f"- **{ex['name']}**")
            output.append(f"  - Sets: {ex['sets']} | Reps: {ex['reps']} | Frequency: {ex['frequency']}")
            output.append(f"  - Notes: {ex['notes']}")
        output.append(f"\n**Restrictions:**\n" + "\n".join(f"  - {r}" for r in phase['restrictions']))
    else:
        # All phases
        for phase in protocol['phases']:
            output.append(f"\n## Phase {phase['phase']}: {phase['name']}")
            output.append(f"**Goals:** {', '.join(phase['goals'])}")
            output.append(f"\n**Key Exercises:**")
            for ex in phase['exercises'][:3]:  # Show first 3 per phase
                output.append(f"  - {ex['name']} ({ex['sets']} sets x {ex['reps']})")
        
        output.append(f"\n## Key Principles")
        for principle in protocol.get('key_principles', []):
            output.append(f"- {principle}")
    
    return "\n".join(output)

# ============================================================================
# MCP TOOLS
# ============================================================================

@mcp.tool(
    name="log_workout",
    annotations={
        "title": "Log Workout Session",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": False
    }
)
async def log_workout(params: LogWorkoutInput) -> str:
    """Log a workout session with AC-joint safety validation and RPE tracking.
    
    This tool records exercise details including sets, reps, weight, and RPE.
    It automatically checks if exercises are safe for AC joint arthritis and
    provides warnings for unsafe movements.
    
    Args:
        params: Workout details including exercise name, sets, reps, weight, RPE, and optional notes
        
    Returns:
        Confirmation with AC-joint safety assessment and suggestions
    """
    try:
        # Check AC joint safety
        safety_check = check_ac_joint_safety(params.exercise_name)
        
        workout_entry = {
            "timestamp": datetime.now().isoformat(),
            "exercise": params.exercise_name,
            "sets": params.sets,
            "reps": params.reps,
            "weight_lbs": params.weight_lbs,
            "rpe": params.rpe.value,
            "notes": params.notes,
            "ac_joint_safe": safety_check["safe"]
        }
        
        if params.response_format == ResponseFormat.JSON:
            return json.dumps({
                "status": "logged",
                "workout": workout_entry,
                "safety_assessment": safety_check
            }, indent=2)
        
        # Markdown format
        output = ["## Workout Logged ✅\n"]
        output.append(f"**Exercise:** {params.exercise_name}")
        output.append(f"**Volume:** {params.sets} sets × {params.reps} reps")
        if params.weight_lbs:
            output.append(f"**Load:** {params.weight_lbs} lbs")
        output.append(f"**Intensity:** {params.rpe.value}")
        if params.notes:
            output.append(f"**Notes:** {params.notes}")
        
        output.append(f"\n### AC Joint Safety Assessment")
        output.append(safety_check["reason"])
        
        if not safety_check["safe"]:
            output.append("\n**💡 AC-Joint Safe Alternatives:**")
            output.append("  - Landmine Press")
            output.append("  - Neutral Grip DB Press (scapular plane)")
            output.append("  - Floor Press")
            output.append("  - Face Pulls / Cable Rows")
        
        return "\n".join(output)
        
    except Exception as e:
        return f"Error logging workout: {str(e)}"

@mcp.tool(
    name="calculate_hydration",
    annotations={
        "title": "Calculate Hydration Needs (Hyperhidrosis-Aware)",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False
    }
)
async def calculate_hydration(params: CalculateHydrationInput) -> str:
    """Calculate hydration and electrolyte needs for hyperhidrosis.
    
    Estimates fluid loss based on workout duration, intensity, temperature, and
    personal sweat rate. Provides sodium/electrolyte recommendations and timing guidance.
    
    Args:
        params: Workout duration, intensity (RPE), temperature, and optional sweat rate
        
    Returns:
        Hydration protocol with fluid volumes, sodium targets, and timing
    """
    try:
        hydration_needs = calculate_hydration_needs(
            params.workout_duration_minutes,
            params.intensity.value,
            params.ambient_temp_f,
            params.sweat_rate_lbs_per_hour
        )
        
        if params.response_format == ResponseFormat.JSON:
            return json.dumps(hydration_needs, indent=2)
        
        # Markdown format
        output = ["## Hydration Protocol 💧\n"]
        output.append(f"**Workout Duration:** {params.workout_duration_minutes} minutes")
        output.append(f"**Intensity:** {params.intensity.value}")
        output.append(f"**Temperature:** {params.ambient_temp_f}°F")
        output.append(f"**Adjusted Sweat Rate:** {hydration_needs['sweat_rate_adjusted']} lbs/hour\n")
        
        output.append(f"### Fluid Loss Estimate")
        output.append(f"- **Total Loss:** {hydration_needs['fluid_loss_lbs']} lbs ({hydration_needs['fluid_loss_oz']} oz)")
        output.append(f"- **Replace:** {hydration_needs['replace_oz_range']} oz")
        output.append(f"- **Timing:** {hydration_needs['timing']}\n")
        
        output.append(f"### Sodium Target")
        output.append(f"- **Sodium:** {hydration_needs['sodium_mg']} mg during/after workout")
        output.append(f"- **Daily Goal (training days):** 3,000-5,000 mg\n")
        
        output.append(f"### Hydration Tips")
        for tip in hydration_needs['tips']:
            output.append(f"  - {tip}")
        
        return "\n".join(output)
        
    except Exception as e:
        return f"Error calculating hydration: {str(e)}"

@mcp.tool(
    name="log_nutrition",
    annotations={
        "title": "Log Meal with Late-Meal Guardrails",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": False
    }
)
async def log_nutrition(params: LogNutritionInput) -> str:
    """Log a meal with automatic late-meal warning system (9pm+ guardrails).
    
    Records meal timing and macronutrients. Provides warnings and recommendations
    for meals after 9pm to prevent late-night eating patterns.
    
    Args:
        params: Meal time, description, and optional macros (protein, carbs, fat, calories)
        
    Returns:
        Confirmation with late-meal warnings if applicable
    """
    try:
        meal_entry = {
            "timestamp": datetime.now().isoformat(),
            "meal_time": params.meal_time,
            "description": params.meal_description,
            "protein_g": params.protein_g,
            "carbs_g": params.carbs_g,
            "fat_g": params.fat_g,
            "calories": params.calories
        }
        
        late_meal_warning = check_late_meal_warning(params.meal_time)
        
        if params.response_format == ResponseFormat.JSON:
            return json.dumps({
                "status": "logged",
                "meal": meal_entry,
                "late_meal_warning": late_meal_warning is not None,
                "warning_message": late_meal_warning
            }, indent=2)
        
        # Markdown format
        output = ["## Meal Logged 🍽️\n"]
        output.append(f"**Time:** {params.meal_time}")
        output.append(f"**Meal:** {params.meal_description}")
        
        if params.protein_g or params.carbs_g or params.fat_g:
            output.append(f"\n**Macros:**")
            if params.protein_g:
                output.append(f"  - Protein: {params.protein_g}g")
            if params.carbs_g:
                output.append(f"  - Carbs: {params.carbs_g}g")
            if params.fat_g:
                output.append(f"  - Fat: {params.fat_g}g")
            if params.calories:
                output.append(f"  - **Total:** {params.calories} cal")
        
        if late_meal_warning:
            output.append(f"\n{late_meal_warning}")
        
        return "\n".join(output)
        
    except Exception as e:
        return f"Error logging nutrition: {str(e)}"

@mcp.tool(
    name="get_exercise_library",
    annotations={
        "title": "Get AC-Joint Safe Exercise Library",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False
    }
)
async def get_exercise_library(params: GetExerciseLibraryInput) -> str:
    """Retrieve exercise library filtered for AC-joint safety and other constraints.
    
    Returns exercises organized by category (pressing, pulling, lower body, etc.)
    that are safe for AC joint arthritis. Emphasizes serratus anterior and lower
    trapezius focus as per training requirements.
    
    Args:
        params: Optional category filter and search term
        
    Returns:
        Filtered exercise list with safety notes
    """
    try:
        exercises_to_show = {}
        
        if params.category:
            # Map category enum to dictionary key
            category_map = {
                ExerciseCategory.PRESSING: "pressing",
                ExerciseCategory.PULLING: "pulling",
                ExerciseCategory.LOWER_BODY: "lower_body_standing",
                ExerciseCategory.SERRATUS_FOCUS: "serratus_lower_trap_focus",
                ExerciseCategory.CORE: "core_standing"
            }
            key = category_map.get(params.category)
            if key and key in AC_JOINT_SAFE_EXERCISES:
                exercises_to_show[params.category.value] = AC_JOINT_SAFE_EXERCISES[key]
        else:
            exercises_to_show = AC_JOINT_SAFE_EXERCISES
        
        # Apply search filter if provided
        if params.search_term:
            filtered = {}
            search_lower = params.search_term.lower()
            for cat, ex_list in exercises_to_show.items():
                matching = [ex for ex in ex_list if search_lower in ex.lower()]
                if matching:
                    filtered[cat] = matching
            exercises_to_show = filtered
        
        if params.response_format == ResponseFormat.JSON:
            return json.dumps({"exercises": exercises_to_show, "unsafe_exercises": AC_JOINT_UNSAFE}, indent=2)
        
        # Markdown format
        output = ["# AC-Joint Safe Exercise Library 💪\n"]
        output.append("**Training Constraints Applied:**")
        output.append("  - Standing/self-stabilizing lifts preferred")
        output.append("  - AC-joint safe pressing (scapular plane, neutral grip)")
        output.append("  - Serratus anterior & lower trapezius emphasis")
        output.append("  - Landmine exercises approved")
        output.append("  - RPE-based progression (6-10 scale)\n")
        
        for category, ex_list in exercises_to_show.items():
            output.append(f"## {category.replace('_', ' ').title()}")
            for exercise in ex_list:
                output.append(f"  - {exercise}")
            output.append("")
        
        output.append("### ❌ Exercises to AVOID:")
        for unsafe in AC_JOINT_UNSAFE:
            output.append(f"  - {unsafe}")
        
        return "\n".join(output)
        
    except Exception as e:
        return f"Error retrieving exercise library: {str(e)}"

@mcp.tool(
    name="get_rehab_protocol",
    annotations={
        "title": "Get Physical Therapy / Rehab Protocol",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False
    }
)
async def get_rehab_protocol(params: GetRehabProtocolInput) -> str:
    """Retrieve evidence-based physical therapy and rehab protocols.
    
    Provides comprehensive PT protocols for:
    - AC joint arthritis
    - Bicep tendonitis
    - Cervical spine arthritis
    - Scapular winging
    - Post-ankle surgery
    - Post-meniscus surgery
    
    Each protocol includes phases, exercises, sets/reps, restrictions, and key principles.
    
    Args:
        params: Condition and optional phase number for detailed view
        
    Returns:
        Complete rehab protocol with exercises, progressions, and clinical notes
    """
    try:
        result = format_rehab_protocol(
            params.condition.value,
            params.phase,
            params.response_format.value
        )
        return result
        
    except Exception as e:
        return f"Error retrieving rehab protocol: {str(e)}"

# ============================================================================
# SERVER ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    mcp.run()
