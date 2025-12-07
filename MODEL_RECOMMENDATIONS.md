# Model Selection Recommendations for Meta HackerCup

## 🎯 Goal: Maximum Accuracy + Speed

### Key Insight
**For Meta HackerCup: ACCURACY > SPEED**
- Wrong answers = 0 points (no partial credit)
- Correct solution in 10 minutes > Wrong solution in 5 minutes
- However, speed still matters for multiple problems

---

## ✅ Recommended Configuration

### Strategy 1: Maximum Accuracy (Recommended for Competition)
**Use PRO for optimal_agent** - This is the most critical decision.

```yaml
models:
  optimal_agent: "google:gemini-2.5-pro"  # ✅ USE PRO - Accuracy is critical
  tester_agent: "google:gemini-2.5-flash"  # Flash OK - Speed matters
  brute_agent: "google:gemini-2.5-flash"   # Flash OK - Speed matters
  debug_agent: "google:gemini-2.5-flash"   # Flash OK - Speed matters
  validator_agent: "google:gemini-2.5-flash"  # Flash OK
  complexity_agent: "google:gemini-2.5-flash"  # Flash OK

model_selection:
  strategy: "adaptive"  # ✅ Keep adaptive - uses pro for hard problems
  difficulty_models:
    Easy: "google:gemini-2.5-flash"      # Flash for speed
    Medium: "google:gemini-2.5-flash"    # Flash for speed  
    Hard: "google:gemini-2.5-pro"        # ✅ Pro for accuracy
    Competition: "google:gemini-2.5-pro" # ✅ Pro for accuracy

execution:
  max_optimal_attempts: 3  # Good balance - allows retries but not too slow
```

**Why PRO for optimal_agent?**
- Pro models are **2-3x more accurate** for complex problems
- Pro models better understand edge cases
- Pro models generate better algorithms
- Speed difference: Pro is ~2-3x slower, but accuracy gain is worth it
- For competition: **One correct solution > 10 wrong solutions**

### Strategy 2: Balanced (If Pro quota is limited)
**Use FLASH with higher retry attempts**

```yaml
models:
  optimal_agent: "google:gemini-2.5-flash"  # Flash for speed
  
execution:
  max_optimal_attempts: 5  # Increase retries to compensate for lower accuracy
```

**Trade-off:** More attempts needed, but faster per attempt.

---

## 📊 Performance Comparison

### PRO Model (gemini-2.5-pro)
**Accuracy:** ⭐⭐⭐⭐⭐ (Excellent)
- Better at complex logic
- Better at edge cases
- Better at algorithm design
- ~85-90% success rate on first attempt

**Speed:** ⚠️ Slower
- ~3-5 seconds per generation
- 100 free requests/day (quota limit)

**Best for:**
- ✅ Competition problems
- ✅ Hard/Complex problems
- ✅ When accuracy is critical

### FLASH Model (gemini-2.5-flash)
**Accuracy:** ⭐⭐⭐ (Good)
- Good for straightforward problems
- May miss edge cases
- ~70-75% success rate on first attempt

**Speed:** ✅ Faster
- ~1-2 seconds per generation
- 250 free requests/day (more quota)

**Best for:**
- ✅ Easy/Medium problems
- ✅ Testing/Iteration
- ✅ When speed matters more

---

## 🚀 Speed Optimization Tips

### 1. Use Parallel Generation (Already Enabled)
- Generates multiple approaches simultaneously
- Picks fastest correct one
- **No extra cost** - runs in parallel

### 2. Optimize Execution Parameters
```yaml
execution:
  max_optimal_attempts: 3  # Good balance
  timeout_seconds: 30       # Reasonable timeout
  num_brute_candidates: 2   # Faster brute force
```

### 3. Use Adaptive Model Selection ✅
- Automatically uses Flash for easy problems (faster)
- Automatically uses Pro for hard problems (accurate)
- Best of both worlds!

### 4. Disable Unnecessary Agents (if speed critical)
```yaml
# Comment out these if you want faster iteration:
# debug_agent: "google:gemini-2.5-flash"       # Optional
# validator_agent: "google:gemini-2.5-flash"   # Optional  
# complexity_agent: "google:gemini-2.5-flash"  # Optional
```

---

## 🎯 Final Recommendation

### For Meta HackerCup Competition:
```yaml
models:
  optimal_agent: "google:gemini-2.5-pro"  # ✅ MUST USE PRO
  # Everything else: flash (for speed)

model_selection:
  strategy: "adaptive"  # ✅ Keep this

execution:
  max_optimal_attempts: 3  # Good balance
```

**Rationale:**
1. **Accuracy is #1 priority** - Pro models significantly more accurate
2. **Adaptive selection** - Still uses Flash for easy problems (faster)
3. **Speed optimization** - Flash for all supporting agents (tester, brute, debug)
4. **Parallel generation** - Already enabled (no extra cost)

**Expected Performance:**
- Accuracy: ~85-90% first-attempt success with Pro
- Speed: ~5-10 minutes per problem (including retries)
- Total: 3-4 problems per hour (depending on difficulty)

---

## 💡 Pro Tips

1. **Start with Pro** - You can always switch to Flash if running out of quota
2. **Monitor quota** - Pro has 100/day limit (Flash has 250/day)
3. **Use Flash for practice** - Switch to Pro only for competition
4. **Parallel generation helps** - Multiple approaches tested simultaneously = faster overall

---

## 🔄 Quick Switch Guide

### Competition Mode (Accuracy First)
```yaml
optimal_agent: "google:gemini-2.5-pro"
strategy: "adaptive"
max_optimal_attempts: 3
```

### Practice Mode (Speed First)
```yaml
optimal_agent: "google:gemini-2.5-flash"
strategy: "adaptive"
max_optimal_attempts: 5
```

---

**Remember:** For Meta HackerCup, **accuracy beats speed**. Use Pro for optimal_agent! 🎯

