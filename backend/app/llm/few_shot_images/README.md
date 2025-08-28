# Few-Shot Training Images

This folder contains curated images for few-shot navigation training.

## Image Files

Place your training images here with descriptive names:

### Required Images:
- `living_room_to_kitchen.png` - Actor in living room, needs to go to kitchen
- `hallway_to_bathroom.png` - Actor in hallway, needs to go to bathroom  
- `inside_bedroom.png` - Actor already in bedroom (task complete scenario)
- `hallway_to_living_room.png` - Actor in hallway, needs to go to living room
- `near_kitchen_entrance.png` - Actor near kitchen entrance
- `ambiguous_corridor.png` - Ambiguous corridor (negative example)

## Setup Instructions

1. **Copy images from captures folder:**
   ```bash
   python setup_few_shot_images.py
   ```

2. **Or manually copy images:**
   - Select your best examples from `blender/captures/`
   - Copy them to this folder
   - Rename them to match the names above

3. **Verify setup:**
   ```bash
   python setup_few_shot_images.py
   # Choose option 2 to validate
   ```

## Image Selection Criteria

Choose images that show:
- **Clear room identification** (furniture visible)
- **Good path planning scenarios** (clear route to destination)
- **Diverse starting positions** (different rooms/locations)
- **One task completion example** (actor already at destination)
- **One negative example** (ambiguous situation)

## Path Planning

For each image, ensure the movement sequence in `few_shot_navigation.py` matches the actual path needed in your house layout:

Example:
```python
"movement_sequence": ["UP", "UP", "UP", "RIGHT", "RIGHT", "RIGHT", "RIGHT", "DOWN", "DOWN"]
```

This should represent the actual steps needed to go from the actor's position in the image to the target room.

## Testing

After setting up images, test the few-shot system:
1. Update the movement sequences to match your house layout
2. Run the Blender Game Engine with few-shot enabled
3. Compare navigation quality before/after few-shot prompting
