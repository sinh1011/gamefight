import pygame

class Fighter():
    def __init__(self, player, x, y, flip, data, sprite_sheet, animation_steps, sound):
        self.player = player
        self.size = data[0]
        self.image_scale = data[1]
        self.offset = data[2]
        self.flip = flip
        self.animation_list = self.load_images(sprite_sheet, animation_steps)
        self.action = 0#0:idle #1:run #2:jump #3:attack1 #4: attack2 #5:hit #6:death
        self.frame_index = 0
        self.image = self.animation_list[self.action][self.frame_index]
        self.update_time = pygame.time.get_ticks()
        self.rect = pygame.Rect((x, y, 80, 180))
        self.vel_y = 0
        self.running = False
        self.jump = False
        self.attacking = False
        self.attack_type = 0
        self.attack_cooldown = 0
        self.attack_sound = sound
        self.hit = False
        self.health = 100
        self.alive = True

    
    def load_images(self, sprite_sheet, animation_steps):
        #extract images from spritesheet
        animation_list = []
        for y, animation in enumerate(animation_steps):
            temp_img_list = []
            for x in range(animation):
                temp_img = sprite_sheet.subsurface(x * self.size, y * self.size, self.size, self.size)
                temp_img_list.append(pygame.transform.scale(temp_img, (self.size * self.image_scale, self.size * self.image_scale)))
            animation_list.append(temp_img_list)
        return animation_list

    def move(self, screen_width, screen_height, surface, target, round_over):
        SPEED = 10
        GRAVITY =2 
        dx = 0
        dy = 0
        self.running =False
        self.attack_type = 0

        # Lấy thông tin phím được nhấn
        key = pygame.key.get_pressed()
        

        #Các hành động thực hiện được khi không bị tấn công
        if self.attacking == False and self.alive ==True and round_over == False:
            #nếu là người chơi 1
            if self.player == 1:
                # Xử lý di chuyển
                if key[pygame.K_a]:
                    dx = -SPEED
                    self.running = True
                if key[pygame.K_d]:
                    dx = SPEED
                    self.running = True

                #nhảy
                if key[pygame.K_w] and self.jump == False:
                    self.vel_y=-30
                    self.jump= True

                #attack
                if key [pygame.K_r] or key [pygame.K_t]:
                    self.attack( target)
                    #chiêu thức sử dụng
                    if key [pygame.K_r]:
                        self.attack_type = 1
                    if key [pygame.K_t]:
                        self.attack_type = 2

            #nếu là người chơi 2
            if self.player == 2:
                # Xử lý di chuyển
                if key[pygame.K_LEFT]:
                    dx = -SPEED
                    self.running = True
                if key[pygame.K_RIGHT]:
                    dx = SPEED
                    self.running = True

                #nhảy
                if key[pygame.K_UP] and self.jump == False:
                    self.vel_y=-30
                    self.jump= True

                #attack
                if key [pygame.K_KP1] or key [pygame.K_KP2]:
                    self.attack( target)
                    #chiêu thức sử dụng
                    if key [pygame.K_KP1]:
                        self.attack_type = 1
                    if key [pygame.K_KP2]:
                        self.attack_type = 2

        #áp dụng trọng lực
        self.vel_y += GRAVITY
        dy += self.vel_y

        #giữ người chơi không bị chạy ra ngoài màn hình
        if self.rect.left + dx < 0:
            dx=self.rect.left
        if self.rect.right + dx > screen_width:
            dx = screen_width - self.rect.right
        if self.rect.bottom + dy > screen_height - 110:
            self.vel_y = 0
            self.jump = False
            dy = screen_height - 110 - self.rect.bottom
        

        # 2 chiến binh luôn đối mặt vào nhau
        if target.rect.centerx > self.rect.centerx:
            self.flip = False
        else:
            self.flip = True

        #dem nguoc thoi gian dung chieu
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        # Cập nhật vị trí của người chơi
        self.rect.x += dx
        self.rect.y += dy

    # Xử lý cập nhật animation
    def update(self):
        if self.health <= 0:
            self.health = 0
            self.alive = False
            self.update_action(6)#6:death
        elif self.hit == True:
            self.update_action(5)#5:hit
        #tan cong chieu thuc
        elif self.attacking == True:
            if self.attack_type == 1:
                self.update_action(3)#3:chieu1
            elif self.attack_type == 2:
                self.update_action(4)#4:chieu2
        #animation nhay
        elif self.jump ==True:
            self.update_action(2)#nhay
        #kiem tra hoat anh dang chay
        elif self.running == True:
            self.update_action(1)#chay
        else:
            self.update_action(0)#dungyen
        # Thời gian chờ giữa các cập nhật animation (miligiây)
        animation_cooldown = 60
        # Cập nhật hình ảnh
        self.image = self.animation_list[self.action][self.frame_index]
         # Kiểm tra xem đã đủ thời gian trôi qua kể từ lần cập nhật cuối cùng hay chưa
        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            self.frame_index += 1
            self.update_time = pygame.time.get_ticks()
        #tạo vòng lặp khi chạy hết hoạt ảnh
        if self.frame_index >= len(self.animation_list[self.action]):
            #if the player is dead then end the animation
            if self.alive == False:
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:
                self.frame_index =0
                #dung lai khi su dung chieu thuc
                if self.action == 3 or self.action == 4:
                    self.attacking = False
                    self.attack_cooldown = 20
                if self.action == 5:
                    self.hit = False
                    #if the player was in the middle of an attack, then the attack is stopped
                    self.attacking = False
                    self.attack_cooldown = 20



    def attack(self, target):
        if self.attack_cooldown == 0:
            self.attacking = True
            self.attack_sound.play()
            attacking_rect = pygame.Rect(self.rect.centerx - (2 * self.rect.width * self.flip), self.rect.y, 2 * self.rect.width, self.rect.height)
            if attacking_rect.colliderect(target.rect):
                target.health -= 10
                target.hit = True

            # pygame.draw.rect(surface, (0, 0, 0), attacking_rect)


    def update_action(self, new_action):
        #check if the new action is different to the previous one
        if new_action != self.action:

            self.action = new_action
            self.attack_sound.play()
            #update the animation settings
            self.frame_index = 0
            self.update_time - pygame.time.get_ticks()


    def draw(self, surface): 
        img = pygame.transform.flip(self.image, self.flip, False)
        # pygame.draw.rect(surface, (102, 255, 82), self.rect)
        surface.blit(img, (self.rect.x - (self.offset[0] * self.image_scale), self.rect.y - (self.offset[1] * self.image_scale)))