import pygame

class SidePanel:
    def __init__(self, screen_offset, width, height, font_size=32):
        self.screen_offset = screen_offset
        self.width = width
        self.height = height
        self.font_size = font_size
        self.font_sizeS = int(font_size/1.5)
        self.font = pygame.font.Font(None, self.font_size)
        self.fontS = pygame.font.Font(None, self.font_sizeS)
        self.surface = pygame.Surface((self.width, self.height))
        self.panel_color = (200, 200, 180)  # Color of the panel
        self.slider_color = (220, 220, 220)  # Color of the panel
        self.sliderhandle_color = (40, 80, 220)
        
        #Slider for the rain
        self.slider_rain_value = 0.5
        self.slider_rain_rect = pygame.Rect(10, 330, self.width - 20, 15)
        self.slider_rain_handle_radius = 10
        self.slider_rain_active = False
        
        self.slider_rainstrength_value = 0.5
        self.slider_rainstrength_rect = pygame.Rect(10, 350, self.width - 20, 15)
        self.slider_rainstrength_handle_radius = 10
        self.slider_rainstrength_active = False

        
        self.environment = None
        self.line = 0
        
    def render(self, clock):
        self.line = 0
        self.surface.fill((self.panel_color))
        
        text_organisms = self.font.render("Organisms:", True, (255,255,255))
        self.surface.blit(text_organisms, (10, 10))
        self.line += 50
        
        for organism in self.environment.organisms:
            text = self.fontS.render(f"R: {organism.rect}", True, (255,255,255))
            self.surface.blit(text, (10, self.line))
            self.line += 20
        
        self.line += 50
        
        text_slider_rain = self.font.render("Rain:", True, (255,255,255))
        self.surface.blit(text_slider_rain, (10, 300))
        
        # Render the slider track
        pygame.draw.rect(self.surface, self.slider_color, self.slider_rain_rect)
        slider_rain_handle_x = int(self.slider_rain_rect.left + self.slider_rain_value * self.slider_rain_rect.width)
        slider_rain_handle_pos = (slider_rain_handle_x, self.slider_rain_rect.centery)
        pygame.draw.circle(self.surface, self.sliderhandle_color, slider_rain_handle_pos, self.slider_rain_handle_radius)
        
        pygame.draw.rect(self.surface, self.slider_color, self.slider_rainstrength_rect)
        slider_rainstrength_handle_x = int(self.slider_rain_rect.left + self.slider_rainstrength_value * self.slider_rainstrength_rect.width)
        slider_rainstrength_handle_pos = (slider_rainstrength_handle_x, self.slider_rainstrength_rect.centery)
        pygame.draw.circle(self.surface, self.sliderhandle_color, slider_rainstrength_handle_pos, self.slider_rainstrength_handle_radius)
       
    def add_environment(self, environment):
        self.environment = environment
     
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            adjusted_pos = (event.pos[0]-self.screen_offset, event.pos[1])
            if self.slider_rain_rect.collidepoint(adjusted_pos):
                self.slider_rain_active = True
            if self.slider_rainstrength_rect.collidepoint(adjusted_pos):
                self.slider_rainstrength_active = True

        if event.type == pygame.MOUSEBUTTONUP:
            self.slider_rain_active = False
            self.slider_rainstrength_active = False
            
        if event.type == pygame.MOUSEMOTION:
            mouse_x = event.pos[0]- self.screen_offset
            if self.slider_rain_active:
                slider_rain_left = self.slider_rain_rect.left
                slider_rain_width = self.slider_rain_rect.width
                normalized_value = (mouse_x - slider_rain_left) / slider_rain_width
                self.slider_rain_value = max(0, min(normalized_value, 1))
                self.environment.rain(self.slider_rain_value*20, self.slider_rainstrength_value*10)
                
            if self.slider_rainstrength_active:
                slider_rainstrength_left = self.slider_rainstrength_rect.left
                slider_rainstrength_width = self.slider_rainstrength_rect.width
                normalized_value = (mouse_x - slider_rainstrength_left) / slider_rainstrength_width
                self.slider_rainstrength_value = max(0, min(normalized_value, 1))
                
                self.environment.rain(self.slider_rain_value*20, self.slider_rainstrength_value*10)
        
    def draw(self, screen, x):
        screen.blit(self.surface, (x, 0))

