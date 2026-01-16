-- Promote the newly registered user to admin
UPDATE user_profiles 
SET role = 'admin' 
WHERE email = 'admin@volunteer.com';
