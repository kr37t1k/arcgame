"""Character physics matching DDNet's CCharacterCore"""
from ..base.vec2 import Vec2
from ..base.collision import CollisionWorld
from ..config import *
from enum import IntEnum

# Where is TUNING_DEFAULTS defined? TODO: /*/*/*///*/*/*/***/*/*/*/*/*/*/*/*

class HookState(IntEnum):
    HOOK_RETRACTED = -1
    HOOK_IDLE = 0
    HOOK_RETRACT_START = 1
    HOOK_RETRACT_END = 3
    HOOK_FLYING = 4
    HOOK_GRABBED = 5


class CoreEvent:
    COREEVENT_GROUND_JUMP = 0x01
    COREEVENT_AIR_JUMP = 0x02
    COREEVENT_HOOK_LAUNCH = 0x04
    COREEVENT_HOOK_ATTACH_PLAYER = 0x08
    COREEVENT_HOOK_ATTACH_GROUND = 0x10
    COREEVENT_HOOK_HIT_NOHOOK = 0x20
    COREEVENT_HOOK_RETRACT = 0x40


class WeaponStat:
    def __init__(self):
        self.m_AmmoRegenStart = 0
        self.m_Ammo = 0
        self.m_Ammocost = 0
        self.m_Got = False


class CharacterPhysics:
    def __init__(self):
        # Physics variables matching CCharacterCore
        self.m_Pos = Vec2(0, 0)
        self.m_Vel = Vec2(0, 0)
        
        self.m_HookPos = Vec2(0, 0)
        self.m_HookDir = Vec2(0, 0)
        self.m_HookTeleBase = Vec2(0, 0)
        self.m_HookTick = 0
        self.m_HookState = HookState.HOOK_IDLE
        self.m_AttachedPlayers = set()
        self.m_HookedPlayer = -1
        
        self.m_ActiveWeapon = 0
        self.m_aWeapons = [WeaponStat() for _ in range(10)]  # NUM_WEAPONS
        
        # Ninja variables
        self.m_Ninja = {
            'm_ActivationDir': Vec2(0, 0),
            'm_ActivationTick': 0,
            'm_CurrentMoveTime': 0,
            'm_OldVelAmount': 0
        }
        
        self.m_NewHook = False
        
        self.m_Jumped = 0
        self.m_JumpedTotal = 0
        self.m_Jumps = 2
        
        self.m_Direction = 0
        self.m_Angle = 0
        self.m_Input = {
            'm_Direction': 0,
            'm_TargetX': 0,
            'm_TargetY': -1,
            'm_Jump': 0,
            'm_Fire': 0,
            'm_Hook': 0
        }
        
        self.m_TriggeredEvents = 0
        
        # World references
        self.m_pWorld = None
        self.m_pCollision = None
        self.m_pTeams = None
        self.m_Id = -1
        self.m_Reset = False
        
        # Collision state
        self.m_Colliding = 0
        self.m_LeftWall = False
        
        # DDNet specific flags
        self.m_Solo = False
        self.m_Jetpack = False
        self.m_CollisionDisabled = False
        self.m_EndlessHook = False
        self.m_EndlessJump = False
        self.m_HammerHitDisabled = False
        self.m_GrenadeHitDisabled = False
        self.m_LaserHitDisabled = False
        self.m_ShotgunHitDisabled = False
        self.m_HookHitDisabled = False
        self.m_Super = False
        self.m_Invincible = False
        self.m_HasTelegunGun = False
        self.m_HasTelegunGrenade = False
        self.m_HasTelegunLaser = False
        self.m_FreezeStart = 0
        self.m_FreezeEnd = 0
        self.m_IsInFreeze = False
        self.m_DeepFrozen = False
        self.m_LiveFrozen = False
        
        # Tuning parameters (default values from DDNet)
        self.m_Tuning = TUNING_DEFAULTS.copy()
        
    def init(self, world, collision, teams=None):
        """Initialize character with world and collision references"""
        self.m_pWorld = world
        self.m_pCollision = collision
        self.m_pTeams = teams
        self.m_Id = -1
        # Set default tuning from world (simplified)
        # In real implementation, this would come from world tuning
        
    def reset(self):
        """Reset character to initial state"""
        self.m_Pos = Vec2(0, 0)
        self.m_Vel = Vec2(0, 0)
        self.m_NewHook = False
        self.m_HookPos = Vec2(0, 0)
        self.m_HookDir = Vec2(0, 0)
        self.m_HookTeleBase = Vec2(0, 0)
        self.m_HookTick = 0
        self.m_HookState = HookState.HOOK_IDLE
        self.set_hooked_player(-1)
        self.m_AttachedPlayers.clear()
        self.m_Jumped = 0
        self.m_JumpedTotal = 0
        self.m_Jumps = 2
        self.m_TriggeredEvents = 0
        
        # DDNet Character
        self.m_Solo = False
        self.m_Jetpack = False
        self.m_CollisionDisabled = False
        self.m_EndlessHook = False
        self.m_EndlessJump = False
        self.m_HammerHitDisabled = False
        self.m_GrenadeHitDisabled = False
        self.m_LaserHitDisabled = False
        self.m_ShotgunHitDisabled = False
        self.m_HookHitDisabled = False
        self.m_Super = False
        self.m_Invincible = False
        self.m_HasTelegunGun = False
        self.m_HasTelegunGrenade = False
        self.m_HasTelegunLaser = False
        self.m_FreezeStart = 0
        self.m_FreezeEnd = 0
        self.m_IsInFreeze = False
        self.m_DeepFrozen = False
        self.m_LiveFrozen = False
        
        # never initialize both to 0
        self.m_Input['m_TargetX'] = 0
        self.m_Input['m_TargetY'] = -1
        
    def set_hooked_player(self, hooked_player):
        """Set the player that this character is hooked to"""
        if hooked_player != self.m_HookedPlayer:
            if self.m_HookedPlayer != -1 and self.m_Id != -1 and self.m_pWorld:
                # Remove from previous hooked player's attached players
                if self.m_pWorld.m_apCharacters[self.m_HookedPlayer]:
                    self.m_pWorld.m_apCharacters[self.m_HookedPlayer].m_AttachedPlayers.discard(self.m_Id)
            
            if hooked_player != -1 and self.m_Id != -1 and self.m_pWorld:
                # Add to new hooked player's attached players
                if self.m_pWorld.m_apCharacters[hooked_player]:
                    self.m_pWorld.m_apCharacters[hooked_player].m_AttachedPlayers.add(self.m_Id)
            
            self.m_HookedPlayer = hooked_player

    def tick(self, use_input=True, do_deferred_tick=True):
        """Main tick function matching DDNet's CCharacterCore::Tick"""
        # Get ground state
        ground_size = 28.0 / 2  # PhysicalSize() / 2
        grounded = (self.m_pCollision.collide_point(Vec2(self.m_Pos.x + ground_size, self.m_Pos.y + ground_size + 5)) or 
                   self.m_pCollision.collide_point(Vec2(self.m_Pos.x - ground_size, self.m_Pos.y + ground_size + 5)))
        
        target_direction = (Vec2(self.m_Input['m_TargetX'], self.m_Input['m_TargetY'])).normalize()
        
        self.m_Vel.y += self.m_Tuning['gravity']
        
        max_speed = self.m_Tuning['ground_control_speed'] if grounded else self.m_Tuning['air_control_speed']
        accel = self.m_Tuning['ground_control_accel'] if grounded else self.m_Tuning['air_control_accel']
        friction = self.m_Tuning['ground_friction'] if grounded else self.m_Tuning['air_friction']
        
        # Handle input
        if use_input:
            self.m_Direction = self.m_Input['m_Direction']
            
            # Setup angle
            import math
            tmp_angle = math.atan2(self.m_Input['m_TargetY'], self.m_Input['m_TargetX'])
            if tmp_angle < -(math.pi / 2.0):
                self.m_Angle = int((tmp_angle + (2.0 * math.pi)) * 256.0)
            else:
                self.m_Angle = int(tmp_angle * 256.0)
            
            # Handle jump
            if self.m_Input['m_Jump']:
                if not (self.m_Jumped & 1):
                    if grounded and (not (self.m_Jumped & 2) or self.m_Jumps != 0):
                        self.m_TriggeredEvents |= CoreEvent.COREEVENT_GROUND_JUMP
                        self.m_Vel.y = -self.m_Tuning['ground_jump_impulse']
                        if self.m_Jumps > 1:
                            self.m_Jumped |= 1
                        else:
                            self.m_Jumped |= 3
                        self.m_JumpedTotal = 0
                    elif not (self.m_Jumped & 2):
                        self.m_TriggeredEvents |= CoreEvent.COREEVENT_AIR_JUMP
                        self.m_Vel.y = -self.m_Tuning['air_jump_impulse']
                        self.m_Jumped |= 3
                        self.m_JumpedTotal += 1
            else:
                self.m_Jumped &= ~1
            
            # Handle hook
            if self.m_Input['m_Hook']:
                if self.m_HookState == HookState.HOOK_IDLE:
                    self.m_HookState = HookState.HOOK_FLYING
                    self.m_HookPos = self.m_Pos + target_direction * 28.0 * 1.5  # PhysicalSize() * 1.5
                    self.m_HookDir = target_direction
                    self.set_hooked_player(-1)
                    self.m_HookTick = 50 * (1.25 - self.m_Tuning['hook_duration'])  # SERVER_TICK_SPEED * (1.25 - hook_duration)
                    self.m_TriggeredEvents |= CoreEvent.COREEVENT_HOOK_LAUNCH
            else:
                self.set_hooked_player(-1)
                self.m_HookState = HookState.HOOK_IDLE
                self.m_HookPos = self.m_Pos
        
        # Handle jumping
        # 1 bit = to keep track if a jump has been made on this input (player is holding space bar)
        # 2 bit = to track if all air-jumps have been used up (tee gets dark feet)
        if grounded:
            self.m_Jumped &= ~2
            self.m_JumpedTotal = 0
        
        # Add the speed modification according to players wanted direction
        if self.m_Direction < 0:
            self.m_Vel.x = self.saturated_add(-max_speed, max_speed, self.m_Vel.x, -accel)
        if self.m_Direction > 0:
            self.m_Vel.x = self.saturated_add(-max_speed, max_speed, self.m_Vel.x, accel)
        if self.m_Direction == 0:
            self.m_Vel.x *= friction
        
        # Do hook
        if self.m_HookState == HookState.HOOK_IDLE:
            self.set_hooked_player(-1)
            self.m_HookPos = self.m_Pos
        elif HookState.HOOK_RETRACT_START <= self.m_HookState < HookState.HOOK_RETRACT_END:
            self.m_HookState += 1
        elif self.m_HookState == HookState.HOOK_RETRACT_END:
            self.m_TriggeredEvents |= CoreEvent.COREEVENT_HOOK_RETRACT
            self.m_HookState = HookState.HOOK_RETRACTED
        elif self.m_HookState == HookState.HOOK_FLYING:
            hook_base = self.m_Pos
            if self.m_NewHook:
                hook_base = self.m_HookTeleBase
            
            new_pos = self.m_HookPos + self.m_HookDir * self.m_Tuning['hook_fire_speed']
            if (new_pos - hook_base).length() > self.m_Tuning['hook_length']:
                self.m_HookState = HookState.HOOK_RETRACT_START
                new_pos = hook_base + (new_pos - hook_base).normalize() * self.m_Tuning['hook_length']
                self.m_Reset = True
            
            # Check against ground (simplified)
            # In real implementation, this would use IntersectLineTeleHook
            
            # Check against other players
            if not self.m_HookHitDisabled and self.m_pWorld and self.m_Tuning['player_hooking']:
                distance = 0.0
                for i in range(64):  # MAX_CLIENTS (simplified)
                    if i >= len(self.m_pWorld.m_apCharacters):
                        continue
                    p_char_core = self.m_pWorld.m_apCharacters[i]
                    if not p_char_core or p_char_core == self or p_char_core.m_Id == -1:
                        continue
                    
                    closest_point = self.closest_point_on_line(self.m_HookPos, new_pos, p_char_core.m_Pos)
                    if (p_char_core.m_Pos - closest_point).length() < 28.0 + 2.0:  # PhysicalSize() + 2.0
                        if self.m_HookedPlayer == -1 or (self.m_HookPos - p_char_core.m_Pos).length() < distance:
                            self.m_TriggeredEvents |= CoreEvent.COREEVENT_HOOK_ATTACH_PLAYER
                            self.m_HookState = HookState.HOOK_GRABBED
                            self.set_hooked_player(i)
                            distance = (self.m_HookPos - p_char_core.m_Pos).length()
            
            if self.m_HookState == HookState.HOOK_FLYING:
                # Check against ground collision
                # Simplified: just check if new_pos is solid
                if self.m_pCollision.collide_point(new_pos):
                    self.m_TriggeredEvents |= CoreEvent.COREEVENT_HOOK_ATTACH_GROUND
                    self.m_HookState = HookState.HOOK_GRABBED
                else:
                    self.m_HookPos = new_pos
        elif self.m_HookState == HookState.HOOK_GRABBED:
            if self.m_HookedPlayer != -1 and self.m_pWorld:
                p_char_core = self.m_pWorld.m_apCharacters[self.m_HookedPlayer]
                if p_char_core and self.m_Id != -1:
                    self.m_HookPos = p_char_core.m_Pos
                else:
                    # Release hook
                    self.set_hooked_player(-1)
                    self.m_HookState = HookState.HOOK_RETRACTED
                    self.m_HookPos = self.m_Pos
            
            # Don't do this hook routine when we are already hooked to a player
            if self.m_HookedPlayer == -1 and (self.m_HookPos - self.m_Pos).length() > 46.0:
                hook_vel = (self.m_HookPos - self.m_Pos).normalize() * self.m_Tuning['hook_drag_accel']
                # The hook has more power to drag you up then down
                if hook_vel.y > 0:
                    hook_vel.y *= 0.3
                
                # The hook will boost its power if the player wants to move in that direction
                if (hook_vel.x < 0 and self.m_Direction < 0) or (hook_vel.x > 0 and self.m_Direction > 0):
                    hook_vel.x *= 0.95
                else:
                    hook_vel.x *= 0.75
                
                new_vel = self.m_Vel + hook_vel
                
                # Check if we are under the legal limit for the hook
                new_vel_length = new_vel.length()
                if new_vel_length < self.m_Tuning['hook_drag_speed'] or new_vel_length < self.m_Vel.length():
                    self.m_Vel = new_vel  # Apply
            
            # Release hook (max default hook time is 1.25 s)
            self.m_HookTick += 1
            if self.m_HookedPlayer != -1 and (self.m_HookTick > 50 + 50 // 5 or  # SERVER_TICK_SPEED + SERVER_TICK_SPEED / 5
                                              (self.m_pWorld and self.m_HookedPlayer >= len(self.m_pWorld.m_apCharacters) or
                                               not self.m_pWorld.m_apCharacters[self.m_HookedPlayer])):
                self.set_hooked_player(-1)
                self.m_HookState = HookState.HOOK_RETRACTED
                self.m_HookPos = self.m_Pos
        
        if do_deferred_tick:
            self.tick_deferred()
    
    def tick_deferred(self):
        """Deferred tick handling player collisions"""
        if self.m_pWorld:
            for i in range(64):  # MAX_CLIENTS (simplified)
                if i >= len(self.m_pWorld.m_apCharacters):
                    continue
                p_char_core = self.m_pWorld.m_apCharacters[i]
                if not p_char_core:
                    continue
                
                if p_char_core == self or (self.m_Id != -1 and not self.m_pTeams.can_collide(self.m_Id, i) if self.m_pTeams else False):
                    continue  # Make sure that we don't nudge our self
                
                if not self.m_Super and not p_char_core.m_Super and (self.m_Solo or p_char_core.m_Solo):
                    continue
                
                # Handle player <-> player collision
                distance = (self.m_Pos - p_char_core.m_Pos).length()
                if distance > 0:
                    dir = (self.m_Pos - p_char_core.m_Pos).normalize()
                    
                    can_collide = (self.m_Super or p_char_core.m_Super) or (
                        not self.m_CollisionDisabled and not p_char_core.m_CollisionDisabled and self.m_Tuning['player_collision']
                    )
                    
                    if can_collide and distance < 28.0 * 1.25:  # PhysicalSize() * 1.25
                        a = (28.0 * 1.45 - distance)
                        velocity = 0.5
                        
                        # Make sure that we don't add excess force by checking the direction against the current velocity
                        if self.m_Vel.length() > 0.0001:
                            velocity = 1 - ((self.m_Vel.normalize().dot(dir) + 1) / 2)
                        
                        self.m_Vel += dir * a * (velocity * 0.75)
                        self.m_Vel *= 0.85
                    
                    # Handle hook influence
                    if not self.m_HookHitDisabled and self.m_HookedPlayer == i and self.m_Tuning['player_hooking']:
                        if distance > 28.0 * 1.50:  # PhysicalSize() * 1.50
                            hook_accel = self.m_Tuning['hook_drag_accel'] * (distance / self.m_Tuning['hook_length'])
                            drag_speed = self.m_Tuning['hook_drag_speed']
                            
                            # Add force to the hooked player
                            temp_x = self.saturated_add(-drag_speed, drag_speed, p_char_core.m_Vel.x, hook_accel * dir.x * 1.5)
                            temp_y = self.saturated_add(-drag_speed, drag_speed, p_char_core.m_Vel.y, hook_accel * dir.y * 1.5)
                            p_char_core.m_Vel = Vec2(temp_x, temp_y)
                            
                            # Add a little bit force to the guy who has the grip
                            temp_x = self.saturated_add(-drag_speed, drag_speed, self.m_Vel.x, -hook_accel * dir.x * 0.25)
                            temp_y = self.saturated_add(-drag_speed, drag_speed, self.m_Vel.y, -hook_accel * dir.y * 0.25)
                            self.m_Vel = Vec2(temp_x, temp_y)
        
        if self.m_HookState != HookState.HOOK_FLYING:
            self.m_NewHook = False
        
        # Clamp the velocity to something sane
        if self.m_Vel.length() > 6000:
            self.m_Vel = self.m_Vel.normalize() * 6000
    
    def move(self):
        """Move character with collision handling - matches DDNet's Move() function"""
        # Calculate velocity ramp
        ramp_value = self.velocity_ramp(self.m_Vel.length() * 50, self.m_Tuning['velramp_start'], 
                                       self.m_Tuning['velramp_range'], self.m_Tuning['velramp_curvature'])
        
        self.m_Vel.x = self.m_Vel.x * ramp_value
        
        new_pos = Vec2(self.m_Pos.x, self.m_Pos.y)
        old_vel = Vec2(self.m_Vel.x, self.m_Vel.y)
        
        # Move the box with collision
        if self.m_pCollision:
            # This is a simplified version of the collision system
            # In real implementation, it would use MoveBox from DDNet collision system
            new_pos, new_vel = self.m_pCollision.move_box(
                new_pos, 
                Vec2(28.0, 28.0),  # PhysicalSizeVec2()
                self.m_Vel
            )
            self.m_Vel = new_vel
            
            # Check if we're grounded after collision
            grounded = (self.m_pCollision.collide_point(Vec2(new_pos.x + 14, new_pos.y + 14 + 5)) or 
                       self.m_pCollision.collide_point(Vec2(new_pos.x - 14, new_pos.y + 14 + 5)))  # +5 offset for ground check
            
            if grounded:
                self.m_Jumped &= ~2
                self.m_JumpedTotal = 0
        else:
            # No collision, just move normally
            new_pos = self.m_Pos + self.m_Vel
        
        # Set collision state
        self.m_Colliding = 0
        if -0.001 < self.m_Vel.x < 0.001:
            if old_vel.x > 0:
                self.m_Colliding = 1
            elif old_vel.x < 0:
                self.m_Colliding = 2
        else:
            self.m_LeftWall = True
        
        # Undo velocity ramp for x component
        self.m_Vel.x = self.m_Vel.x * (1.0 / ramp_value)
        
        # Player collision check (simplified)
        if self.m_pWorld and (self.m_Super or (self.m_Tuning['player_collision'] and not self.m_CollisionDisabled and not self.m_Solo)):
            distance = (new_pos - self.m_Pos).length()
            if distance > 0:
                end = int(distance) + 1
                last_pos = Vec2(self.m_Pos.x, self.m_Pos.y)
                
                for i in range(end):
                    a = i / distance
                    pos = self.m_Pos + (new_pos - self.m_Pos) * a
                    
                    for p in range(64):  # MAX_CLIENTS (simplified)
                        if p >= len(self.m_pWorld.m_apCharacters):
                            continue
                        p_char_core = self.m_pWorld.m_apCharacters[p]
                        if not p_char_core or p_char_core == self:
                            continue
                        if not p_char_core.m_Super and (self.m_Solo or p_char_core.m_Solo or 
                                                        p_char_core.m_CollisionDisabled or 
                                                        (self.m_Id != -1 and not self.m_pTeams.can_collide(self.m_Id, p) if self.m_pTeams else False)):
                            continue
                        
                        d = (pos - p_char_core.m_Pos).length()
                        if d < 28.0:  # PhysicalSize()
                            if a > 0.0:
                                self.m_Pos = last_pos
                            elif (new_pos - p_char_core.m_Pos).length() > d:
                                self.m_Pos = new_pos
                            return
                    
                    last_pos = pos
        
        self.m_Pos = new_pos
    
    def saturated_add(self, min_val, max_val, current, modifier):
        """Add with saturation - matches DDNet's SaturatedAdd function"""
        if modifier < 0:
            if current < min_val:
                return current
            current += modifier
            if current < min_val:
                current = min_val
            return current
        else:
            if current > max_val:
                return current
            current += modifier
            if current > max_val:
                current = max_val
            return current
    
    def velocity_ramp(self, value, start, range_val, curvature):
        """Calculate velocity ramp - matches DDNet's VelocityRamp function"""
        if value < start:
            return 1.0
        import math
        return 1.0 / math.pow(curvature, (value - start) / range_val)
    
    def closest_point_on_line(self, start, end, point):
        """Find closest point on line segment to a point - matches DDNet's closest_point_on_line"""
        from ..base.vec2 import closest_point_on_line
        return closest_point_on_line(start, end, point)