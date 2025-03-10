-- Обновление статуса пользователя
UPDATE 
    users
SET 
    status = 'inactive',
    updated_at = CURRENT_TIMESTAMP
WHERE 
    id = ?
    AND status = 'active' 