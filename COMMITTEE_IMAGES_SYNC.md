# Committee Images Sync Summary

## Issue Resolved
✅ Committee members page photos partially restored. **Baby Kuriakose** photo now displays.

## What Was Done

### 1. Production Media Sync
- Copied entire production media tree from `wesly-server:~/app/Backend/media` → `Backend/media_from_prod`
- Included all subdirectories: `members/photos/`, `committee/photos/`, `gallery/`, etc.
- **Result**: ~60+ media files copied locally (~150MB total)

### 2. Production Database Analysis
- Exported live Postgres database from production container → `Backend/live_family_db.sql`
- Scanned DB for committee photo references for term_label='2026-28'
- **Found 3 committee members with photo fields set:**
  - Baby Kuriakose: `committee/photos/baby_kuriakose.jpeg` ✅ (file exists)
  - Korula Issac: `committee/photos/korula.jpeg` ❌ (file does NOT exist on server)
  - Saju Elias: `committee/photos/saju_eleas.jpeg` ❌ (file does NOT exist on server)

### 3. Local Database Update
- Created Django management command: `sync_committee_photos.py`
- Command maps production photo references to local media files
- Only syncs photos where files actually exist (Baby Kuriakose)
- **Result**: Baby Kuriakose photo path set in local DB

## Current Status

### Photos Updated (1)
| Member | Photo Path | Status |
|--------|-----------|--------|
| Baby Kuriakose | committee/photos/baby_kuriakose.jpeg | ✅ Ready |

### Photos Missing (2)
| Member | Photo Path | Issue |
|--------|-----------|-------|
| Korula Issac | committee/photos/korula.jpeg | File doesn't exist on production server |
| Saju Elias | committee/photos/saju_eleas.jpeg | File doesn't exist on production server |

### Other Committee Members (9)
All other committee members have no photo set in the local database.

## Files Created/Modified
- **New**: `Backend/families/management/commands/sync_committee_photos.py` — Management command to sync photos
- **Modified**: `Backend/db.sqlite3` — Updated Baby Kuriakose record with photo path
- **Created**: `Backend/media/` — Contains synced production media including `committee/photos/baby_kuriakose.jpeg`
- **Created**: `Backend/live_family_db.sql` — Live production database dump (reference)
- **Created**: `Backend/media_from_prod/` — Staging copy of production media

## Next Steps (If Needed)

### To Display More Committee Photos:
1. **Obtain missing photo files** from the user or production backups (korula.jpeg, saju_eleas.jpeg)
2. Place them in `Backend/media/committee/photos/`
3. Re-run the management command: `python manage.py sync_committee_photos`

### To Add Photos for Other Committee Members:
1. Gather photos for Anish Chacko, Manoj Andrews, etc.
2. Place them in `Backend/media/committee/photos/` with appropriate filenames
3. Update `PHOTO_MAPPING` in the management command
4. Re-run the command

### To Verify in Frontend:
- Backend API should now return photo_url for Baby Kuriakose when calling committee endpoint
- Frontend will construct the media URL as: `http://localhost:8000/media/committee/photos/baby_kuriakose.jpeg`
- Image should display in committee members page

## Testing
To verify the sync worked:
```bash
cd Backend
python manage.py shell
>>> from families.models import FamilyCommitteeMember
>>> m = FamilyCommitteeMember.objects.get(name='Baby Kuriakose', term_label='2026-28')
>>> m.photo
# Should show: committee/photos/baby_kuriakose.jpeg
```

## Database Info
- **Local**: SQLite at Backend/db.sqlite3
- **Production**: PostgreSQL (family_db) on wesly-server container app-db-1
- **Live dump**: Backend/live_family_db.sql (for reference/comparison)
- **Backup**: Backend/backup_2026-05-02.sql (daily snapshot from wesly-server)
