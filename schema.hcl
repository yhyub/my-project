schema "coze_db" {
  charset = "utf8mb4"
  collate = "utf8mb4_unicode_ci"
}

table "users" {
  schema = schema.coze_db
  column "id" {
    type = int
    auto_increment = true
    primary_key = true
  }
  column "username" {
    type = varchar(255)
    unique = true
    not_null = true
  }
  column "email" {
    type = varchar(255)
    unique = true
    not_null = true
  }
  column "password_hash" {
    type = varchar(255)
    not_null = true
  }
  column "created_at" {
    type = timestamp
    default = current_timestamp
  }
  column "updated_at" {
    type = timestamp
    default = current_timestamp
    on_update = current_timestamp
  }
  index "idx_email" {
    columns = [column.email]
    unique = true
  }
}

table "workflows" {
  schema = schema.coze_db
  column "id" {
    type = int
    auto_increment = true
    primary_key = true
  }
  column "name" {
    type = varchar(255)
    not_null = true
  }
  column "description" {
    type = text
  }
  column "user_id" {
    type = int
    not_null = true
    references = table.users.column.id
    on_delete = cascade
  }
  column "definition" {
    type = json
    not_null = true
  }
  column "created_at" {
    type = timestamp
    default = current_timestamp
  }
  column "updated_at" {
    type = timestamp
    default = current_timestamp
    on_update = current_timestamp
  }
  index "idx_user_id" {
    columns = [column.user_id]
  }
}

table "plugins" {
  schema = schema.coze_db
  column "id" {
    type = int
    auto_increment = true
    primary_key = true
  }
  column "name" {
    type = varchar(255)
    not_null = true
  }
  column "description" {
    type = text
  }
  column "version" {
    type = varchar(50)
    not_null = true
  }
  column "definition" {
    type = json
    not_null = true
  }
  column "created_at" {
    type = timestamp
    default = current_timestamp
  }
  column "updated_at" {
    type = timestamp
    default = current_timestamp
    on_update = current_timestamp
  }
}

table "bot_configs" {
  schema = schema.coze_db
  column "id" {
    type = int
    auto_increment = true
    primary_key = true
  }
  column "name" {
    type = varchar(255)
    not_null = true
  }
  column "description" {
    type = text
  }
  column "user_id" {
    type = int
    not_null = true
    references = table.users.column.id
    on_delete = cascade
  }
  column "config" {
    type = json
    not_null = true
  }
  column "created_at" {
    type = timestamp
    default = current_timestamp
  }
  column "updated_at" {
    type = timestamp
    default = current_timestamp
    on_update = current_timestamp
  }
  index "idx_bot_user_id" {
    columns = [column.user_id]
  }
}