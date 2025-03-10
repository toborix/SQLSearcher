-- Получение списка активных пользователей
SELECT 
    id,
    username,
    email,
    created_at,
    last_login_at
FROM 
    users
WHERE 
    status = 'active'
    AND deleted_at IS NULL
ORDER BY 
    last_login_at DESC
LIMIT 100 